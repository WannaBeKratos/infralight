{{ il_group("network", label="VPC Network", icon="cloud", color="#42A5F5") }}

{{ il_node("vpc", label="Main VPC", icon="cloud", group="network") }}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "infralight-vpc"
  }
}

{{ il_node("pub_subnet", label="Public Subnet", icon="dns", group="network") }}
{{ il_edge("vpc", "pub_subnet", label="10.0.1.0/24") }}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet"
  }
}

{{ il_node("priv_subnet", label="Private Subnet", icon="lock", group="network") }}
{{ il_edge("vpc", "priv_subnet", label="10.0.2.0/24") }}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "private-subnet"
  }
}

{{ il_group("compute", label="Compute", icon="memory", color="#FF7043") }}

{{ il_node("web", label="Web Server", icon="dns", group="compute") }}
{{ il_edge("pub_subnet", "web", label="hosts") }}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id

  tags = {
    Name = "web-server"
  }
}

{{ il_node("db", label="RDS Database", icon="database", group="compute") }}
{{ il_edge("priv_subnet", "db", label="hosts") }}
{{ il_edge("web", "db", label="port 5432", style="dashed") }}

resource "aws_db_instance" "main" {
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  db_name           = "appdb"
  username          = "admin"
  password          = var.db_password

  db_subnet_group_name = aws_db_subnet_group.main.name

  tags = {
    Name = "main-database"
  }
}

{{ il_node("igw", label="Internet Gateway", icon="public", group="network") }}
{{ il_edge("igw", "vpc", label="internet") }}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

{{ il_note("AWS infrastructure managed by Infralight", target="vpc") }}

variable "db_password" {
  type      = string
  sensitive = true
}

output "vpc_id" {
  value = aws_vpc.main.id
}

output "web_public_ip" {
  value = aws_instance.web.public_ip
}
