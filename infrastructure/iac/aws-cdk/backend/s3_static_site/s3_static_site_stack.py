"""
Stack for creating static websites hosted in S3.

Stack Architecture
--------------------

.. drawio-image:: /_static/infrastructure/static-site-stack.drawio
    :format: svg
"""


import aws_cdk as cdk
from aws_cdk import aws_certificatemanager as certificatemanaager
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as cloudfront_origins
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_s3 as s3
from constructs import Construct


class S3StaticSiteStack(cdk.Stack):
    """
    Define infrastructure for a static site in an S3 bucket.

    .. note::

        This stack uses a CloudFront distribution to cache the site in many
        geolocations and apply HTTPS. At the time Eric created this stack,
        he wasn't sure whether this was strictly necesary.

        There may be other ways to achieve HTTPS for an S3 static site
        without having to pay for the CloudFront distribution cost.

    :param domain_name: like ``rootski.io``
    :param subdomain: like ``docs`` so that we have ``docs.rootski.io``
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        domain_name: str,
        subdomain: str,
        **kwargs,
    ):
        """
        Initialize an S3 static site object.

        :param iam_access_key_id: key_id with programmatic access that will be
            present in the user-data.sh script
        :param iam_access_key: same as above but the actual key

        The IAM key and key id are used to access the S3 bucket where database backups are kept.
        """
        super().__init__(scope, construct_id, **kwargs)

        fully_qualified_domain_name = f"{subdomain}.{domain_name}"

        #: bucket for the static website HTML/CSS/JS files
        bucket = s3.Bucket(
            self,
            id="static-site-bucket",
            bucket_name=fully_qualified_domain_name,
            access_control=s3.BucketAccessControl.PUBLIC_READ,
            website_index_document="index.html",
            website_error_document="error.html",
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        hosted_zone_of_domain = route53.HostedZone.from_lookup(
            self,
            id=f"HostedZone-{subdomain}",
            domain_name=domain_name,
        )

        #: TLS/SSL certificate used to give HTTPS to the fully qualified domain name
        dns_verified_cert = certificatemanaager.DnsValidatedCertificate(
            self,
            id="dns-verified-cert",
            hosted_zone=hosted_zone_of_domain,
            domain_name=fully_qualified_domain_name,
        )

        #: CDN to cache the website files in edge locations for faster page loads
        cloudfront_distribution = cloudfront.Distribution(
            self,
            id="static-site-distribution",
            price_class=cloudfront.PriceClass.PRICE_CLASS_ALL,
            certificate=dns_verified_cert,
            default_behavior=cloudfront.BehaviorOptions(
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                compress=True,
                origin=cloudfront_origins.S3Origin(bucket=bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=[fully_qualified_domain_name],
        )

        #: DNS rule to map the FQDN to the cloudfront distribution
        route53.RecordSet(
            self,
            id=f"{subdomain}-record",
            record_type=route53.RecordType.A,
            zone=hosted_zone_of_domain,
            record_name=fully_qualified_domain_name,
            target=route53.RecordTarget.from_alias(
                alias_target=route53_targets.CloudFrontTarget(distribution=cloudfront_distribution)
            ),
        )

        # cdk.CfnOutput(
        #     self,
        #     id="FullyQualifiedDomainName",
        #     value=fully_qualified_domain_name,
        #     # description=f"Map {fully_qualified_domain_name} to s3://{bucket.bucket_name}"
        # )
        cdk.CfnOutput(
            self,
            id="CloudfrontID",
            value=cloudfront_distribution.distribution_id,
            description="ID of the cloudfront distribution; can be used to invalidate the distribution and refresh the S3 files",
        )
        cdk.CfnOutput(
            self,
            id="BucketName",
            value=bucket.bucket_name,
            description="ID of the cloudfront distribution; can be used to invalidate the distribution and refresh the S3 files",
        )
