"""
This program creates an EC2 instance in a specified subnet and VPC, and then 
installs a HANA Express database on it. The parameters for the instance are
stored in a file - param.txt. HANA Express is a free trial version from SAP on the instance.
Download intructions for Hana Express 2.0 are here https://developers.sap.com/tutorials/hxe-ua-register.html
"""

import boto3
import os
import sys

# Check if a file name has been provided as a command line argument
if len(sys.argv) < 2:
    print("Please provide a file name as a command line argument.")
    sys.exit(1)

# Check if the provided file exists
file_name = sys.argv[1]
if not os.path.isfile(file_name):
    print("The provided file does not exist.")
    sys.exit(1)

# Read the file and set the parameters
with open(file_name, 'r') as f:
    lines = f.readlines()

parameters = {}
for line in lines:
    name, value = line.strip().split('=')
    parameters[name] = value

# Set the parameters from the file
hostname = parameters.get('hostname')
region_name = parameters.get('region_name')
tar_file = parameters.get('tar_file')
tar_file_name = parameters.get('tar_file_name')
iam_instance_profile = parameters.get('iam_instance_profile')
bucket_name = parameters.get('bucket_name')
media_directory = parameters.get('media_directory')
instance_type = parameters.get('instance_type')
keyname = parameters.get('keyname')
imageid = parameters.get('imageid')
install_dir = parameters.get('install_dir')
system_id = parameters.get('system_id')
instance_num = parameters.get('instance_num')
password = parameters.get('password')
setup_exe = parameters.get('setup_exe')
subnet_id = parameters.get('subnet_id')

# If sg_group is a string representation of a list, convert it to a list
sg_group = parameters.get('sg_group')
if isinstance(sg_group, str):
    # Remove brackets, split by comma, and strip whitespace
    sg_group = [group.strip() for group in sg_group.strip('[]').split(',')]

# If public_ip_address is a string representation of a boolean, convert it to a boolean
public_ip_address = parameters.get('public_ip_address')
if isinstance(public_ip_address, str):
    public_ip_address = public_ip_address.lower() == 'true'

# Create an EC2 client
ec2 = boto3.resource('ec2', region_name=region_name)

# Create a user data script - install Hana Express
user_data_script = f"""#!/bin/bash -x
# Set the hostname
hostnamectl set-hostname --static {hostname}

# Get the private IP of the instance
PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)

# Get the hostname from instance metadata
full_hostname=$(curl -s http://169.254.169.254/latest/meta-data/local-hostname)

# Remove the hostname part and assign the remaining part to new_full_hostname
new_full_hostname=$(echo $full_hostname | cut -d'.' -f2-)

# Replace the 'internal hostname' part with the custom hostname
custom_hostname={hostname}.$new_full_hostname
tmphostname={hostname}

# Add the mapping to /etc/hosts
echo "$PRIVATE_IP $tmphostname $custom_hostname" >> /etc/hosts

# Create the sapmedia directory
mkdir -p {media_directory}

# Change permissions for the sapmedia directory
chmod 777 {media_directory}

# Update the system
zypper update -y

# Install the required packages
zypper install -y libgcc_s1 libstdc++6 libatomic1

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Copy file from S3 to /hana/sapmedia
aws s3 cp {bucket_name}{tar_file_name} {media_directory}/

# Extract the SAR file
tar -xvzf {tar_file} -C {media_directory}

cd {media_directory}

# Create an expect script
cat << EOF > setup_hxe.expect
#!/usr/bin/expect -f
# Set variables
set timeout -1
set INSTALL_DIR "{install_dir}"
set SYSTEM_ID "{system_id}"
set INSTANCE_NUM "{instance_num}"
set HOST_NAME "{hostname}"
set PASSWORD "{password}"

# Start the setup script
spawn {media_directory}/{setup_exe}

# Respond to prompts
expect "HANA, express edition installer root directory"
send "\$INSTALL_DIR\r"
expect "Enter SAP HANA system ID"
send "\$SYSTEM_ID\r"
expect "Enter instance number"
send "\$INSTANCE_NUM\r"
expect "Enter local host name"
send "\$HOST_NAME\r"
expect "Enter HDB master password"
send "\$PASSWORD\r"
expect "Confirm \\\"HDB master\\\" password"
send "\$PASSWORD\r"
expect "Proceed with installation? (Y/N)"
send "Y\r"
send "\r"
expect
EOF

# Make the expect script executable
chmod +x setup_hxe.expect

# Run the expect script
{media_directory}/setup_hxe.expect
"""

# Create an EC2 instance with the user data script and the specified parameters
instances = ec2.create_instances(
    ImageId=imageid,
    MinCount=1,
    MaxCount=1,
    InstanceType=instance_type,
    KeyName=keyname,
    UserData=user_data_script,
    IamInstanceProfile={
        'Name': iam_instance_profile
    },
    BlockDeviceMappings=[
        {
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'VolumeSize': 30,
                'VolumeType': 'gp2'
            }
        }
    ],
    NetworkInterfaces=[{
        'SubnetId': subnet_id,
        'DeviceIndex': 0,
        'Groups': sg_group,  # Replace with your security group ID - only support 1 for now
        'AssociatePublicIpAddress': public_ip_address
    }]
)

# Add a tag to the created instance(s)
for instance in instances:
    instance.create_tags(Tags=[{'Key': 'Name', 'Value': 'HanaExpress2'}])

# Print the instance ID of the created instance(s)
print(f"Instance created successfully - {instances[0].id}")