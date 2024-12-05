from opensearchpy import OpenSearch

host = 'localhost'
port = 9200
auth = ('admin', '@Hydro420') # For testing only. Don't store credentials in code.

# Create the client with SSL/TLS enabled, but hostname verification disabled.
client = OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_compress = True, # enables gzip compression for request bodies
    use_ssl = False,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)

try:
    response = client.info()
    print("Connected to OpenSearch:", response)
except Exception as e:
    print("Error connecting to OpenSearch:", e)
