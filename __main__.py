"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

staging_vpc = aws.ec2.Vpc(resource_name="staging_vpc", cidr_block="10.0.0.0/16", enable_dns_support="true", enable_dns_hostnames="false")

private_cidrs = aws.ec2.Subnet("private_cidrs",
    cidr_block="10.0.0.0/19",
    map_public_ip_on_launch=False,
    tags={
        "Name": "private-cidrs",
    },
    vpc_id=staging_vpc.id)

public_cidrs = aws.ec2.Subnet("public_cidrs",
    cidr_block="10.0.128.0/20",
    map_public_ip_on_launch=False,
    tags={
        "Name": "public-cidrs",
    },
    vpc_id=staging_vpc.id)
    
staging_key = aws.ec2.KeyPair("staging_key", public_key="<FULL AWS GENERATED PUBLIC KEY>")

local_traffic_sg = aws.ec2.SecurityGroup("local_traffic_sg",
    description="local_traffic_sg",
    vpc_id=staging_vpc.id,
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        description="local traffic ingress",
        from_port=0,
        to_port=0,
        protocol="tcp",
        cidr_blocks=[public_cidrs.cidr_block],
    )],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
    )],
    tags={
        "Name": "local traffic ssh",
    })

external_traffic_sg = aws.ec2.SecurityGroup("external_traffic_sg",
    description="external_traffic_sg",
    vpc_id=staging_vpc.id,
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        description="external ssh",
        from_port=22,
        to_port=22,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
    ), aws.ec2.SecurityGroupIngressArgs(
        description="external ping",
        from_port=0,
        to_port=0,
        protocol="icmp",
        cidr_blocks=["0.0.0.0/0"],
    )],
    tags={
        "Name": "external traffic ssh",
    })
#ubuntu 20 lts ami
web = aws.ec2.Instance("web-server",
    ami="ami-0ca5c3bd5a268e7db",
    instance_type="t2.micro",
    subnet_id=public_cidrs.id,
    vpc_security_group_ids=[local_traffic_sg.id,external_traffic_sg.id],
    key_name=staging_key,
    tags={
        "Name": "Web Server",
    })

# Export 
pulumi.export('staging_vpc_name', staging_vpc.id)
pulumi.export('private_cidrs', private_cidrs.id)
pulumi.export('public_cidrs', public_cidrs.id)
pulumi.export('local_sg', local_traffic_sg.id)
pulumi.export('external_sg', external_traffic_sg.id)
pulumi.export('web-server', web.id)
