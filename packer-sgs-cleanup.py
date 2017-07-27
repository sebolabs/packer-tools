# FROM: https://github.com/sebolabs/
# This is run periodically to delete obsolete temporary AWS security groups created by Packer
# 
# To provide:
# - AWS region
# - VPC ID
# 
# Delete obsolete SGs when:
# - SG description is 'Temporary group for Packer'

import boto3
import json
from botocore.exceptions import ClientError

# fixed variables
dryrun_enabled = False
aws_region = '<unknown>' # AWS region
vpc_id = '<unknown>' # VPC used by Packer
sg_filter = [{"Name":"description", "Values": ["Temporary group for Packer"]}]

# ec2 connection
ec2_conn = boto3.client('ec2', region_name=aws_region)
ec2_resource_conn = boto3.resource('ec2', region_name=aws_region)

def get_packer_obsolete_sgs():
  sgs_to_delete = []
  vpc = ec2_resource_conn.Vpc(id=vpc_id)
  print '[info] searching for obsolete SGs...'
  for sg in vpc.security_groups.filter(Filters=sg_filter):
    sgs_to_delete.append(sg.id)
  return sgs_to_delete

def delete_sgs(sgs_ids):
  print '[info] deleting obsolete SGs...'
  for sg_id in sgs_ids:
    try:
      ec2_conn.delete_security_group(DryRun=dryrun_enabled, GroupId=sg_id)
    except ClientError as error:
      print '[error] '+str(error)
      raise

def main():
  if dryrun_enabled:
    print "\n!!! the script runs in 'dry-run' mode !!!\n"
  sgs_ids_to_delete = get_packer_obsolete_sgs()
  sgs_count = len(sgs_ids_to_delete)
  if sgs_count != 0:
    sgs_json_data = ec2_conn.describe_security_groups(GroupIds=sgs_ids_to_delete)
    for json_sg in sgs_json_data['SecurityGroups']:
      print 'ID: '+json_sg['GroupId']+' | Name: '+json_sg['GroupName']+' | Description: '+json_sg['Description']
    delete_sgs(sgs_ids_to_delete)
    print '[ok] '+str(sgs_count)+' SGs deleted'
  else:
    print '[info] no obsolete SGs found'

if __name__ =='__main__':main()
