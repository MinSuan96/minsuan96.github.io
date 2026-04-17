---
Title: TLS vs SSH for Communication
author: Teh Min Suan
date: 12 September 2025
---

# TLS vs SSH for Communication

## How TLS Works

TLS (Transport Layer Security) is a cryptographic protocol that provides secure communication over a network. It operates on top of TCP and consists of several phases:

### TLS Handshake Process
1. **Client Hello**: Client initiates connection, sends supported cipher suites and TLS version
2. **Server Hello**: Server responds with chosen cipher suite and sends server certificate
3. **Certificate Verification**: Client verifies server certificate against trusted Certificate Authorities (CAs)
4. **Key Exchange**: Client and server establish shared encryption keys using algorithms like ECDHE or RSA
5. **Client Certificate** (Optional): Server requests client certificate for mutual authentication
6. **Finished Messages**: Both parties confirm handshake completion
7. **Secure Communication**: Encrypted data transmission begins using established session keys

### TLS Security Features
- **Encryption**: All application data encrypted using symmetric algorithms (AES, ChaCha20)
- **Authentication**: Identity verification through X.509 certificates
- **Integrity**: Message authentication codes (MAC) prevent data tampering
- **Forward Secrecy**: Session keys are ephemeral and cannot be compromised retroactively

## Server and Client Certificates

### Server Certificate
- **Purpose**: Proves server identity to connecting clients
- **Contains**: Server's public key, domain name, issuer information, validity period
- **Validation**: Clients verify against trusted Certificate Authority (CA) chain
- **Required**: Always needed for TLS connections

### Client Certificate
- **Purpose**: Proves client identity to server (mutual TLS/mTLS)
- **Contains**: Client's public key, client identifier, issuer information, validity period
- **Validation**: Server verifies against trusted CA or predefined client certificate list
- **Optional**: Only required for mutual TLS authentication

### Certificate Generation

#### Creating a Certificate Authority (CA)
```bash
# Generate CA private key
openssl genrsa -out ca-key.pem 4096

# Create CA certificate
openssl req -new -x509 -days 3650 -key ca-key.pem -out ca-cert.pem
```

#### Generating Server Certificate
```bash
# Generate server private key
openssl genrsa -out server-key.pem 4096

# Create certificate signing request (CSR)
openssl req -new -key server-key.pem -out server.csr

# Sign server certificate with CA
openssl x509 -req -days 365 -in server.csr -CA ca-cert.pem -CAkey ca-key.pem -out server-cert.pem -CAcreateserial
```

#### Generating Client Certificate
```bash
# Generate client private key
openssl genrsa -out client-key.pem 4096

# Create client certificate signing request
openssl req -new -key client-key.pem -out client.csr

# Sign client certificate with CA
# Sign client certificate with CA
openssl x509 -req -days 365 -in client.csr -CA ca-cert.pem -CAkey ca-key.pem -out client-cert.pem -CAcreateserial
```

## Important Considerations

### Certificate Rotation
- **Mandatory Requirement**: Certificates have expiration dates and must be rotated
- **Automation Needed**: Implement automated certificate renewal (Let's Encrypt, internal CA)
- **Planned Downtime**: Certificate updates may require service restarts
- **Monitoring**: Track certificate expiration dates to prevent service interruption

### TLS vs mTLS Decision
#### Standard TLS (Server Certificate Only)
- **Simpler Implementation**: Only server needs certificate
- **Application Auth**: If required, client authentication handled at application layer

#### Mutual TLS (Client + Server Certificates)
- **Stronger Security**: Both parties authenticate with certificates
- **No Shared Secrets**: Eliminates passwords or keys
- **Complex Management**: Must distribute and manage client certificates on all sensors (Note: current SSH implementation uses the same public/private key pair for all sensors, which is simpler but less secure. Similarly, you could use the same client certificate for all sensors, but this is not recommended as it eliminates individual sensor identification and compromises security if one sensor is breached)
- **Recommended When**: Maximum security required, centralized certificate management available

### Port Configuration
- **Avoid Port 441**: Already used by existing SSH service
- **Standard TLS Ports**: Consider 443 (HTTPS), 8443, or custom high port (e.g., 8000-9000)
- **Firewall Rules**: Update firewall to allow new TLS port
- **Port Documentation**: Clearly document chosen port for operational procedures

### Implementation Checklist
1. **Choose TLS vs mTLS** based on security requirements and management complexity
2. **Select unused port** (not 441) for TLS service
3. **Set up Certificate Authority** or use existing PKI infrastructure
4. **Generate server certificate** for analytics server
5. **Generate client certificates** if using mTLS
6. **Implement certificate rotation** mechanism
7. **Configure load balancer** for sensor connection distribution if required
8. **Update firewall rules** for new TLS port
9. **Test reconnection scenarios** to verify faster recovery
10. **Monitor certificate expiration** to prevent service disruption

## Advantages of TCP with TLS vs SSH for Message Transmission

### Performance Benefits
- **Lower Overhead**: TLS has less protocol overhead compared to SSH
- **Optimized for Data Transfer**: Designed specifically for efficient data transmission
- **Better Throughput**: Generally achieves higher data transfer rates
- **Scalability**: More suitable for high-volume message transmission

### Implementation Simplicity
- **Simpler Protocol Stack**: Less complex than SSH's multiple layers
- **Standard Libraries**: Widely available TLS libraries in most programming languages
- **Certificate Management**: Standard PKI infrastructure for authentication

### Resource Efficiency
- **Lower CPU Usage**: Less computational overhead for encryption/decryption
- **Memory Efficiency**: Smaller memory footprint per connection
- **Connection Reuse**: TLS connections can be efficiently reused for multiple messages

## Disadvantages of TCP with TLS vs SSH for Message Transmission

### Security Considerations
- **Certificate Management Complexity**: Need to manage certificate lifecycle and revocation unless using the same client certificate for all sensors (not recommended)
- **No Built-in Authentication**: Requires separate implementation of user authentication unless using mTLS (Note: current SSH implementation uses the same public/private key pair for all sensors, which is simpler but less secure. Similarly, you could use the same client certificate for all sensors, but this is not recommended as it eliminates individual sensor identification and compromises security if one sensor is breached)

### Operational Challenges
- **No Shell Integration**: Cannot leverage existing SSH infrastructure and tools
- **Custom Implementation Required**: Need to build application-level protocols on top of TLS
- **Key Management**: A typical secure TLS deployment (especially with mutual TLS) expects a full Public Key Infrastructure (PKI) (Note: current SSH implementation uses the same public/private key pair for all sensors, which is simpler but less secure. Similarly, you could use the same client certificate for all sensors, but this is not recommended as it eliminates individual sensor identification and compromises security if one sensor is breached)
- **Monitoring**: Fewer standard tools for monitoring and debugging compared to SSH

### Infrastructure Requirements
- **Certificate Authority**: Requires CA infrastructure or self-signed certificate management
- **Port Management**: Need to manage separate ports and firewall rules

## Security Model Differences

### Standard TLS (Server-Only Authentication)
```
Application Layer    [Custom Authentication & Authorization]
TLS Layer           [Encryption + Server Authentication]
TCP Layer           [Reliable Transport]
IP Layer            [Network Routing]
```

### Mutual TLS (Client + Server Authentication)
```
Application Layer    [Optional Additional Authorization]
TLS Layer           [Encryption + Mutual Authentication (Client & Server Certificates)]
TCP Layer           [Reliable Transport]
IP Layer            [Network Routing]
```

### SSH Security (Restricted Account)
```
SSH Application     [Built-in User Auth + Access Control]
SSH Transport       [Encryption + Mutual Authentication]
TCP Layer          [Reliable Transport]
IP Layer           [Network Routing]
```

## Scenario Analysis: Sensor to Analytics Server Communication

### Use Case Description
- **Primary Flow**: Sensors collect logs and transmit to analytics server (high volume, continuous)
- **Secondary Flow**: Analytics server occasionally sends configuration/commands to sensors (low volume, infrequent)
- **Requirements**: Secure transmission, efficient log streaming, minimal sensor resource usage

### TCP with TLS Analysis for Sensor Communication

#### Advantages
- **High Throughput**: Excellent for continuous log streaming from multiple sensors
- **Resource Efficiency**: Lower CPU and memory usage on resource-constrained sensors
- **Connection Persistence**: Long-lived connections ideal for continuous data streaming
- **Batching Support**: Can efficiently batch multiple log entries in single transmission
- **Scalability**: Analytics server can handle thousands of concurrent sensor connections
- **Protocol Flexibility**: Can implement custom protocols optimized for log data format
- **Compression**: Easy to implement data compression to reduce bandwidth usage

#### Disadvantages
- **Certificate Management**: Must distribute and manage certificates on potentially thousands of sensors
- **Connection Recovery**: Need custom logic to handle connection drops and reconnection

### SSH Analysis for Sensor Communication

#### Advantages
- **Established Infrastructure**: Can leverage existing SSH tools and monitoring
- **Simple Implementation**: Standard SSH libraries handle connection management
- **Access Control**: Built-in user and command restrictions
- **Robust Recovery**: SSH handles connection drops and reconnection automatically

#### Disadvantages
- **Higher Resource Usage**: More CPU and memory intensive on sensors
- **Protocol Overhead**: SSH has more overhead than pure TLS for data transmission
- **Throughput Limitations**: Lower maximum throughput compared to optimized TLS implementation
- **Connection Limits**: SSH servers may have lower concurrent connection limits
- **Complexity for Streaming**: Not optimized for continuous data streaming

### Implementation Recommendations

#### Choose TCP with TLS When:
- **High Volume Logging**: Sensors generate >100MB logs per day
- **Many Sensors**: Deploying >1000 sensors
- **Resource Constraints**: Sensors have limited CPU/memory (IoT devices, embedded systems)
- **Real-time Analytics**: Require low-latency log transmission
- **Custom Protocol Benefits**: Need specialized data formats or compression

#### Choose SSH When:
- **Existing SSH Infrastructure**: Already have SSH-based management systems
- **Frequent Bidirectional Communication**: Regular server-to-sensor commands needed
- **Simple Deployment**: Limited development resources for custom protocols
- **Mixed Use Cases**: Sensors also used for remote administration
- **Security Priority**: Maximum security with minimal custom implementation

### Hybrid Architecture Consideration

#### Dual Protocol Approach
```
Primary Channel (TCP/TLS): Sensor → Analytics Server (Log Streaming)
Command Channel (SSH):     Analytics Server → Sensor (Configuration/Commands)
```

**Benefits:**
- Optimize each channel for its specific use case
- High-performance log streaming with reliable command delivery
- Leverage strengths of both protocols

**Drawbacks:**
- Increased complexity in implementation and maintenance
- More ports and firewall rules to manage
- Dual authentication mechanisms to maintain

### Performance Metrics Comparison

| Metric | TCP with TLS | SSH |
|--------|--------------|-----|
| Throughput | 95-100% of raw TCP | 70-85% of raw TCP |
| CPU Usage (Sensor) | Low | Medium-High |
| Memory Usage (Sensor) | Low | Medium |
| Connection Setup Time | Fast | Slower |
| Concurrent Connections | Very High (10K+) | Medium (1K-5K) |
| Bidirectional Ease | Complex | Simple |

## Conclusion

For sensor-to-analytics server communication, **TCP with TLS is generally preferred** for the primary log streaming due to its superior performance and resource efficiency. However, **SSH may be better for the occasional server-to-sensor communication** due to its built-in bidirectional capabilities and simpler implementation.

TCP with TLS offers superior performance and efficiency for high-volume message transmission scenarios, while SSH with restricted accounts provides better out-of-the-box security features and simpler deployment in existing infrastructure. The choice depends on specific requirements around performance, security model, and operational complexity.

