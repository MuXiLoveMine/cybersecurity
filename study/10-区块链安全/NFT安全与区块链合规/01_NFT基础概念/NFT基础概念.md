# NFT基础概念

### 1.1 NFT定义与技术原理

NFT（Non-Fungible Token，非同质化代币）是区块链上表示唯一数字资产所有权的加密令牌。与ERC-20等同质化代币不同，每个NFT具有唯一标识符，不可互换，适合表示数字艺术品、收藏品、游戏道具、虚拟地产等独特资产。

NFT的技术原理可分解为以下层次：

- **链上合约层**：NFT通过智能合约实现，合约维护tokenId到owner的映射，记录每个NFT的当前所有者、元数据URI和交易历史。
- **资产表示层**：每个NFT由tokenId唯一标识， tokenId在合约内全局唯一。合约通过mint（铸造）函数创建新的tokenId。
- **元数据层**：NFT的"内容"（图片、视频、属性等）通常不存储在链上，而是通过元数据URI指向链下存储位置。
- **存储层**：NFT的实际媒体文件和元数据JSON存储在IPFS、Arweave、中心化服务器等链下位置。
- **交易层**：NFT通过合约的transfer函数实现所有权转移，交易在链上永久记录。

### 1.2 ERC标准详解

#### 1.2.1 ERC-721

ERC-721是最早的NFT标准，由CryptoKitties团队提出：

- **核心接口**：
  - `balanceOf(owner)`：查询某地址持有的NFT数量。
  - `ownerOf(tokenId)`：查询某NFT的当前所有者。
  - `transferFrom(from, to, tokenId)`：转移NFT所有权。
  - `approve(approved, tokenId)`：授权某地址可转移特定NFT。
  - `setApprovalForAll(operator, approved)`：授权某地址管理所有NFT。
  - `tokenURI(tokenId)`：返回NFT的元数据URI。
  - `safeTransferFrom`：安全转移，目标需实现ERC-721接收接口（否则回退）。

- **安全特性**：
  - `safeTransferFrom`检查目标地址是否为合约，若是合约则要求实现`onERC721Received`，防止NFT被锁定到无法处理NFT的合约。
  - Transfer事件在每次转移时必须触发，便于链上追踪。
  - mint和burn函数未在标准中强制定义，由实现者自行处理。

- **局限性**：每次转移一个NFT需一次交易，批量操作Gas费高。

#### 1.2.2 ERC-1155

ERC-1155是半同质化代币标准，由Enjin团队提出：

- **核心创新**：一个合约可同时管理多种代币（同质化和非同质化），每个tokenId可对应多个实例（supply）。
  - `balanceOf(owner, id)`：查询某地址对某tokenId的持有量。
  - `balanceOfBatch(owners, ids)`：批量查询多个地址对多个tokenId的持有量。
  - `safeBatchTransferFrom(from, to, ids, values, data)`：批量转移多种代币。

- **优势**：
  - 批量转移：一次交易可转移多种代币，大幅降低Gas费。
  - 节省部署成本：一个合约管理整个游戏或收藏品系列。
  - 灵活性：同 tokenId可以是唯一的NFT（supply=1）也可以是同质化代币（supply>1）。

- **安全特性**：
  - 同样有safeTransferFrom和safeBatchTransferFrom，检查目标合约是否实现onERC1155Received/onERC1155BatchReceived。
  - 批量操作时如果任何一项失败则整个交易回退。

#### 1.2.3 ERC-998

ERC-998是可组合NFT标准（Composable NFT）：

- 允许NFT拥有其他NFT或ERC-20代币，形成层级结构。
- 转移父NFT时，所有子资产自动一起转移。
- 核心接口包括顶层 ERC-998（管理NFT子资产）和ERC-998 ERC-20（管理ERC-20子资产）。
- 使用场景：游戏角色NFT拥有装备NFT和游戏币。
- 安全考量：子资产转移权限管理、层级遍历的Gas消耗、避免循环引用。

### 1.3 NFT元数据存储

NFT的元数据和媒体文件的存储方式直接决定其持久性和去中心化程度：

#### 1.3.1 链上存储

- 所有元数据和媒体数据直接存储在智能合约中（如Art Blocks、CryptoPunks部分数据）。
- 优势：数据永久存在于链上，不依赖外部存储。
- 劣势：Gas费极高，仅适合简单数据（像素艺术、文本）。
- 实现方式：将图像编码为SVG或Base64字符串存储在合约中。

#### 1.3.2 IPFS

- IPFS（InterPlanetary File System）是基于内容寻址的P2P文件系统。
- 文件通过CID（Content Identifier）唯一标识，CID由文件内容哈希生成。
- 优势：去中心化、内容不可篡改（CID绑定内容）、可永久访问（只要有节点存储）。
- 劣势：文件需要被pin（固定存储）才能持续可用，否则可能被垃圾回收。
- NFT最佳实践：在IPFS上存储元数据JSON和媒体文件，将IPFS URI（ipfs://CID）存储在合约的tokenURI中。
- Pinning服务：Pinata、Infura、NFT.storage提供IPFS固定服务。

#### 1.3.3 Arweave

- Arweave是一次付费永久存储的区块链。
- 文件上传时支付一次性费用，Arweave通过捐赠模型保证长期存储。
- 优势：真正永久的去中心化存储，无需持续pin。
- 劣势：上传费用较高，网络存储容量有限。
- NFT使用：Koii、Metaplex等NFT平台使用Arweave存储元数据。

#### 1.3.4 中心化服务器

- 许多NFT项目的元数据和媒体存储在AWS、Cloudflare等中心化服务器。
- 风险：服务器关闭或被入侵后NFT变成"空壳"；运营方可随时更换图片内容。
- 这是NFT生态中最受批评的存储方式，损害了NFT的持久性承诺。

### 1.4 NFT交易市场架构

NFT交易市场是连接买家、卖家和NFT合约的平台：

- **链上结算**：交易通过智能合约在链上完成所有权转移和资金结算。
- **链下撮合**：订单簿通常在链下维护（如OpenSea的Seaport协议），通过签名授权进行链上结算。
- ** royalty机制**：EIP-2981标准定义NFT版税机制，每次二级市场交易时自动支付创作者版税。
- **Wyvern协议**：早期OpenSea使用的交易协议，支持多种交易模式（固定价、拍卖、打包交易）。
- **Seaport协议**：OpenSea 2022年推出的新协议，更灵活、Gas效率更高，支持多资产交换（可用ERC-20、其他NFT作为交换媒介）。

---

---

