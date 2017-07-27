# FROM: https://github.com/sebolabs/
# This is run periodically to terminate obsolete AWS instances created by Packer
# 
# # To provide:
# - AWS region
# 
# Terminate obsolete instances when (and):
# - instance tag:Name is 'Packer Builder'
# - instance is running
# - instance launch date is in the past

import boto3
import datetime
from botocore.exceptions import ClientError

# fixed variables
dryrun_enabled = False
aws_region = '<unknown>' # AWS region
ec2_filters = [ { 'Name': 'tag:Name', 'Values': ['Packer Builder']}, 
                { 'Name': 'instance-state-name', 'Values': ['running']} ]

# ec2 client connection
ec2_conn = boto3.client('ec2', region_name=aws_region)

def get_obsolete_packer_instances():
  instances_to_terminate = []
  response = ec2_conn.describe_instances(Filters=ec2_filters)
  print '[info] searching for obsolete instances...'
  for r in response['Reservations']:
    for i in r['Instances']:
      if i['LaunchTime'].date() < datetime.datetime.now().date():
        instances_to_terminate.append(i['InstanceId'])  
        print 'ID: '+i['InstanceId']+' | LAUNCH_TIME: '+str(i['LaunchTime'])+' | AMI_ID: '+i['ImageId']
  return instances_to_terminate

def terminate_instances(instance_ids):
  print '[info] terminating obsolete instances...'
  try:
    ec2_conn.terminate_instances(DryRun=dryrun_enabled, InstanceIds=instance_ids)
  except ClientError as error:
    print '[error] '+str(error)
    raise

def main():
  if dryrun_enabled:
    print "\n!!! the script runs in 'dry-run' mode !!!\n"
  instance_ids_to_terminate = get_obsolete_packer_instances()
  instance_count = len(instance_ids_to_terminate)
  if instance_count != 0:
    terminate_instances(instance_ids_to_terminate)
    print '[ok] '+str(instance_count)+' instances terminated'
  else:
    print '[info] no obsolete instances found'

if __name__ =='__main__':main()
