import jsonobject


class TerraformConfig(jsonobject.JsonObject):
    allow_dynamic_properties = False
    aws_profile = jsonobject.StringProperty(default='default')
    state_bucket = jsonobject.StringProperty()
    state_bucket_region = jsonobject.StringProperty()
    region = jsonobject.StringProperty()
    environment = jsonobject.StringProperty()
    azs = jsonobject.ListProperty(str)
    vpc_begin_range = jsonobject.StringProperty()
    external_routes = jsonobject.ListProperty(lambda: ExternalRouteConfig)
    servers = jsonobject.ListProperty(lambda: ServerConfig)
    proxy_servers = jsonobject.ListProperty(lambda: ServerConfig)
    rds_instances = jsonobject.ListProperty(lambda: RdsInstanceConfig)


class ExternalRouteConfig(jsonobject.JsonObject):
    allow_dynamic_properties = False
    cidr_block = jsonobject.StringProperty()
    gateway_id = jsonobject.StringProperty()


class ServerConfig(jsonobject.JsonObject):
    allow_dynamic_properties = False
    server_name = jsonobject.StringProperty()
    server_instance_type = jsonobject.StringProperty()
    network_tier = jsonobject.StringProperty(choices=['app-private', 'public', 'db-private'])
    az = jsonobject.StringProperty(choices=['a', 'b', 'c'])
    volume_size = jsonobject.IntegerProperty(default=20)


class RdsInstanceConfig(jsonobject.JsonObject):
    allow_dynamic_properties = False
    identifier = jsonobject.StringProperty()
    instance_type = jsonobject.StringProperty()  # should start with 'db.'
    storage = jsonobject.IntegerProperty()
