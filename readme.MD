Parameters description:

- `region_name`: The AWS region where the EC2 instance will be launched. (e.g. "us-west-2")
- `hostname`: The hostname or IP address of the HANA instance. (e.g. "hanatest02")
- `password`: The password for the HANA instance. (e.g. "mypassword")
- `tar_file`: The path to the HANA installation archive file. (must be "/hana/sapmedia/hxe.tgz")
- `tar_file_name`: The name of the HANA installation archive file. (must be "hxe.tgz")
- `iam_instance_profile`: The IAM instance profile with S3 access permissions. (e.g. "hana-s3-readonly-access")
- `bucket_name`: The S3 bucket where the HANA installation media will be stored. (e.g. "hana-installation-media")
- `media_directory`: The directory on the HANA instance where the installation media will be extracted. (e.g. "/hana/media")
- `instance_type`: The EC2 instance type for the HANA instance. (e.g. "c4.xlarge")
- `keyname`: The key pair name used for SSH access to the EC2 instance. (e.g. "my-keypair")
- `imageid`: The ID of the Amazon Machine Image (AMI) used to launch the EC2 instance. (only tested with SUSE for SAP - "ami-0df509852b5f3f98c" this one is for us-east-2)
- `install_dir`: HANA, express edition installer root directory - automatically created by the tar -avfz (e.g. "/hana/sapmedia/HANA_EXPRESS_20")
- `system_id`: The system ID for the HANA instance. (e.g. "HDB")
- `instance_num`: The instance number for the HANA instance. (e.g. "00")
- `setup_exe`: The name of the setup script for HANA Express Edition. (hardcoded part of setup for Hana Express "setup_hxe.sh")
- `subnet_id`: The ID of the subnet where the EC2 instance will be launched. (e.g. "subnet-12345678")
- `sg_group`: The ID of the security group for the EC2 instance. (e.g. use only one for now "sg-12345678")
- `public_ip_address`: Whether to assign a public IP address to the EC2 instance. (e.g. "true")
Example:
region_name=us-east-2
hostname=hanacp05
password=MyPasswdChangeMe@321
tar_file=/hana/sapmedia/hxe.tgz
tar_file_name=hxe.tgz
iam_instance_profile=s3-full-readonly-access
bucket_name=s3://sapinstallmedia/
media_directory=/hana/sapmedia
instance_type=c4.xlarge
keyname=MyKey
imageid=ami-0df509852b5f3f98c
install_dir=/hana/sapmedia/HANA_EXPRESS_20
system_id=HXE
instance_num=90
setup_exe=setup_hxe.sh
subnet_id=subnet-xxxxxxxxxxxxxxxxe
sg_group=sg-yyyyyyyyyyyyyyyyy
public_ip_address=True