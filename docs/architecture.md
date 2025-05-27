# Архитектура Xray VPN Server

## Общая схема системы

```mermaid
graph TB
    subgraph "Клиенты"
        C1[Windows Client<br/>v2rayN]
        C2[Android Client<br/>v2rayNG]
        C3[iOS Client<br/>Shadowrocket]
        C4[Linux Client<br/>v2rayA]
    end
    
    subgraph "Интернет"
        DNS[DNS Server<br/>example.com → YOUR_SERVER_IP]
        LE[Let's Encrypt<br/>SSL Certificates]
    end
    
    subgraph "VPS Server (YOUR_SERVER_IP)"
        subgraph "Docker Containers"
            XR[Xray Server<br/>Port 443<br/>VLESS+XTLS+Vision+REALITY]
            NG[Nginx<br/>Port 80<br/>Fallback Server]
            CB[Certbot<br/>SSL Management]
        end
        
        subgraph "Volumes"
            SSL[SSL Certificates<br/>/data/certbot/conf]
            WWW[Website Files<br/>/data/www]
            CFG[Configurations<br/>/config]
        end
    end
    
    subgraph "Fallback Target"
        MS[Microsoft.com<br/>Real HTTPS Server]
    end
    
    C1 -.->|VLESS+REALITY| XR
    C2 -.->|VLESS+REALITY| XR
    C3 -.->|VLESS+REALITY| XR
    C4 -.->|VLESS+REALITY| XR
    
    XR -->|Fallback Traffic| NG
    XR -.->|SNI: microsoft.com| MS
    
    NG --> WWW
    CB --> SSL
    CB <--> LE
    
    DNS --> XR
    
    style XR fill:#e1f5fe
    style NG fill:#f3e5f5
    style CB fill:#e8f5e8
    style MS fill:#fff3e0
```

## Поток трафика

```mermaid
sequenceDiagram
    participant Client
    participant Xray
    participant Nginx
    participant Microsoft
    participant Internet
    
    Note over Client,Microsoft: Обычное VPN подключение
    Client->>+Xray: VLESS+REALITY (SNI: microsoft.com)
    Xray->>+Internet: Encrypted VPN Traffic
    Internet-->>-Xray: Response
    Xray-->>-Client: Decrypted Response
    
    Note over Client,Microsoft: Fallback при обнаружении
    Client->>+Xray: Invalid/Detected Traffic
    Xray->>+Nginx: Fallback to port 8080
    Nginx-->>-Xray: Website Content
    Xray-->>-Client: Looks like normal website
    
    Note over Client,Microsoft: Прямое подключение к Microsoft
    Client->>+Microsoft: Direct HTTPS (if redirected)
    Microsoft-->>-Client: Real Microsoft Content
```

## Компоненты системы

```mermaid
graph LR
    subgraph "Генерация конфигураций"
        KG[Key Generator<br/>UUID, X25519, ShortID]
        CG[Config Generator<br/>Xray, Nginx configs]
        TG[Template Engine<br/>Jinja2 templates]
    end
    
    subgraph "Управление"
        CLI[CLI Interface<br/>Click commands]
        ENV[Environment<br/>.env variables]
        UTIL[Utilities<br/>Validation, Setup]
    end
    
    subgraph "Развертывание"
        DC[Docker Compose<br/>Service orchestration]
        DF[Dockerfile<br/>Config generator image]
        VOL[Volumes<br/>Persistent data]
    end
    
    CLI --> KG
    CLI --> CG
    CG --> TG
    CLI --> ENV
    CLI --> UTIL
    
    DC --> VOL
    DF --> CG
    
    style KG fill:#ffebee
    style CG fill:#e8f5e8
    style CLI fill:#e3f2fd
```

## Безопасность

```mermaid
graph TD
    subgraph "Уровни защиты"
        L1[Level 1: REALITY<br/>Traffic Masquerading]
        L2[Level 2: XTLS+Vision<br/>Advanced Encryption]
        L3[Level 3: Fallback<br/>Website Simulation]
        L4[Level 4: SSL/TLS<br/>Certificate Validation]
        L5[Level 5: Firewall<br/>Port Restrictions]
    end
    
    subgraph "Методы обнаружения"
        DPI[Deep Packet Inspection]
        SNI[SNI Analysis]
        TLS[TLS Fingerprinting]
        STAT[Statistical Analysis]
    end
    
    L1 -.->|Blocks| DPI
    L1 -.->|Blocks| SNI
    L2 -.->|Blocks| TLS
    L3 -.->|Blocks| STAT
    L4 -.->|Validates| SNI
    L5 -.->|Limits| DPI
    
    style L1 fill:#c8e6c9
    style L2 fill:#bbdefb
    style L3 fill:#d1c4e9
    style L4 fill:#ffcdd2
    style L5 fill:#fff9c4
```

## Протокол REALITY

```mermaid
graph TB
    subgraph "REALITY Handshake"
        CH[Client Hello<br/>SNI: microsoft.com]
        SH[Server Hello<br/>Real Microsoft Cert]
        AUTH[Authentication<br/>Private Key Validation]
        EST[Connection Established<br/>or Fallback]
    end
    
    subgraph "Результаты"
        VPN[VPN Connection<br/>Authenticated Client]
        FB[Fallback<br/>Website Content]
        REAL[Real Microsoft<br/>Redirected Traffic]
    end
    
    CH --> SH
    SH --> AUTH
    AUTH -->|Valid Key| VPN
    AUTH -->|Invalid Key| FB
    AUTH -->|Suspicious| REAL
    
    style VPN fill:#c8e6c9
    style FB fill:#fff3e0
    style REAL fill:#ffcdd2
```

## Мониторинг и логирование

```mermaid
graph LR
    subgraph "Источники логов"
        XL[Xray Logs<br/>Connection info]
        NL[Nginx Logs<br/>Access logs]
        CL[Certbot Logs<br/>SSL renewal]
        DL[Docker Logs<br/>Container status]
    end
    
    subgraph "Мониторинг"
        STATS[Xray Stats API<br/>Traffic statistics]
        HEALTH[Health Checks<br/>Service status]
        ALERTS[Alerts<br/>Error notifications]
    end
    
    XL --> STATS
    NL --> HEALTH
    CL --> HEALTH
    DL --> HEALTH
    
    STATS --> ALERTS
    HEALTH --> ALERTS
    
    style STATS fill:#e8f5e8
    style HEALTH fill:#fff3e0
    style ALERTS fill:#ffebee
``` 