"""
Crypto Education Module - EXPANDED VERSION
Provides comprehensive explanations for 18+ crypto concepts
Supports both English and Vietnamese
With question variation mapping for multiple phrasings
"""

# Question variations - maps multiple phrasings to base concepts
variations = {
    # ─── English: Bitcoin core ───────────────────────────────────────────────
    "what is bitcoin": "bitcoin",
    "explain bitcoin": "bitcoin",
    "tell me about bitcoin": "bitcoin",
    "bitcoin basics": "bitcoin",
    "bitcoin intro": "bitcoin",
    "how does bitcoin work": "bitcoin",
    "what makes bitcoin valuable": "bitcoin",
    "bitcoin overview": "bitcoin",
    "bitcoin summary": "bitcoin",
    # Bitcoin market
    "bitcoin market": "bitcoin_market",
    "bitcoin market cap": "bitcoin_market",
    "how big is bitcoin market": "bitcoin_market",
    "bitcoin trading": "bitcoin_market",
    "bitcoin market overview": "bitcoin_market",
    # Bitcoin price
    "bitcoin price": "bitcoin_price",
    "btc price": "bitcoin_price",
    "how much is bitcoin": "bitcoin_price",
    "current bitcoin price": "bitcoin_price",
    "bitcoin value": "bitcoin_price",
    "what drives bitcoin price": "bitcoin_price",
    "why does bitcoin price change": "bitcoin_price",
    "bitcoin price history": "bitcoin_price",
    "bitcoin ath": "bitcoin_price",
    # Bitcoin wallet
    "bitcoin wallet": "bitcoin_wallet",
    "btc wallet": "bitcoin_wallet",
    "how to store bitcoin": "bitcoin_wallet",
    "store bitcoin safely": "bitcoin_wallet",
    # Bitcoin mining
    "bitcoin mining": "bitcoin_mining",
    "mining": "bitcoin_mining",
    "how to mine bitcoin": "bitcoin_mining",
    "is mining profitable": "bitcoin_mining",
    "mining bitcoin profitable": "bitcoin_mining",
    "bitcoin miner": "bitcoin_mining",
    # Blockchain
    "blockchain": "blockchain",
    "what is blockchain": "blockchain",
    "how does blockchain work": "blockchain",
    "blockchain technology": "blockchain",
    "bitcoin blockchain": "bitcoin_blockchain",
    # Halving
    "halving": "halving",
    "bitcoin halving": "halving",
    "what is halving": "halving",
    "halving effect on price": "halving",
    "next halving": "halving",
    # Decentralization
    "decentralization": "decentralization",
    "decentralized": "decentralization",
    "what is decentralization": "decentralization",
    # Smart contract
    "smart contract": "smart_contract",
    "smart contracts": "smart_contract",
    "what is smart contract": "smart_contract",
    # DeFi
    "defi": "defi",
    "decentralized finance": "defi",
    "what is defi": "defi",
    "defi explained": "defi",
    # Ethereum
    "ethereum": "ethereum",
    "what is ethereum": "ethereum",
    "eth": "ethereum",
    "ethereum vs bitcoin": "ethereum",
    # Altcoin
    "altcoin": "altcoin",
    "altcoins": "altcoin",
    "what are altcoins": "altcoin",
    # Wallet
    "wallet": "wallet",
    "crypto wallet": "wallet",
    "what is a crypto wallet": "wallet",
    "hot wallet cold wallet": "wallet",
    # Exchange
    "exchange": "exchange",
    "crypto exchange": "exchange",
    "what is a crypto exchange": "exchange",
    "binance": "exchange",
    "coinbase": "exchange",
    # Volatility
    "volatility": "volatility",
    "crypto volatility": "volatility",
    "why is crypto volatile": "volatility",
    "price swings": "volatility",
    # Crypto market general
    "crypto market": "crypto_market",
    "what is crypto market": "crypto_market",
    "cryptocurrency market": "crypto_market",
    "what is the crypto market": "crypto_market",
    "how does crypto market work": "crypto_market",
    "market": "crypto_market",
    "what is the market": "crypto_market",
    # Market directions
    "bull market": "bull_market",
    "what is bull market": "bull_market",
    "bull run": "bull_market",
    "crypto bull": "bull_market",
    "bear market": "bear_market",
    "what is bear market": "bear_market",
    "crypto bear": "bear_market",
    "bear run": "bear_market",
    # Cryptocurrency
    "cryptocurrency": "cryptocurrency",
    "crypto": "cryptocurrency",
    "what is cryptocurrency": "cryptocurrency",
    "how does cryptocurrency work": "cryptocurrency",
    # ─── English: New concepts ───────────────────────────────────────────────
    # DCA
    "dca": "dca",
    "dollar cost averaging": "dca",
    "what is dca": "dca",
    "dca strategy": "dca",
    "how to dca": "dca",
    "dca crypto": "dca",
    "buy dip": "dca",
    "regular buying": "dca",
    # HODL
    "hodl": "hodl",
    "what is hodl": "hodl",
    "hodl strategy": "hodl",
    "should i hold bitcoin": "hodl",
    "hold bitcoin": "hodl",
    "long term hold": "hodl",
    "hold crypto": "hodl",
    # FOMO / FUD
    "fomo": "fomo_fud",
    "fud": "fomo_fud",
    "what is fomo": "fomo_fud",
    "what is fud": "fomo_fud",
    "fomo fud": "fomo_fud",
    "fear of missing out": "fomo_fud",
    "fear uncertainty doubt": "fomo_fud",
    # ATH / ATL
    "ath": "ath_atl",
    "atl": "ath_atl",
    "all time high": "ath_atl",
    "all time low": "ath_atl",
    "bitcoin all time high": "ath_atl",
    "crypto record price": "ath_atl",
    # Staking
    "staking": "staking",
    "what is staking": "staking",
    "crypto staking": "staking",
    "how to stake": "staking",
    "earn from staking": "staking",
    "proof of stake": "staking",
    "pos": "staking",
    # NFT
    "nft": "nft",
    "nfts": "nft",
    "what is nft": "nft",
    "non fungible token": "nft",
    "non-fungible token": "nft",
    "how do nfts work": "nft",
    "nft explained": "nft",
    # Layer 2
    "layer 2": "layer2",
    "layer2": "layer2",
    "lightning network": "layer2",
    "bitcoin lightning": "layer2",
    "what is layer 2": "layer2",
    "scaling bitcoin": "layer2",
    # Gas fee
    "gas fee": "gas_fee",
    "gas fees": "gas_fee",
    "what is gas fee": "gas_fee",
    "ethereum gas": "gas_fee",
    "transaction fee": "gas_fee",
    "network fee": "gas_fee",
    "why are gas fees so high": "gas_fee",
    # Market cap
    "market cap": "market_cap",
    "market capitalization": "market_cap",
    "what is market cap": "market_cap",
    "bitcoin market cap": "market_cap",
    "crypto market cap": "market_cap",
    "circulating supply": "market_cap",
    # Whale
    "whale": "whale",
    "crypto whale": "whale",
    "what is a whale": "whale",
    "bitcoin whale": "whale",
    "whale manipulation": "whale",
    "big holder": "whale",
    # Leverage
    "leverage": "leverage",
    "margin trading": "leverage",
    "what is leverage": "leverage",
    "futures bitcoin": "leverage",
    "liquidation": "leverage",
    "long short": "leverage",
    "what is liquidation": "leverage",
    # Whitepaper
    "whitepaper": "whitepaper",
    "bitcoin whitepaper": "whitepaper",
    "satoshi whitepaper": "whitepaper",
    "what is whitepaper": "whitepaper",
    "original bitcoin paper": "whitepaper",

    # ─── Vietnamese: Bitcoin core ─────────────────────────────────────────────
    "bitcoin": "bitcoin",
    "bitcoin là gì": "bitcoin",
    "giải thích bitcoin": "bitcoin",
    "bitcoin hoạt động như thế nào": "bitcoin",
    "bitcoin là loại tiền gì": "bitcoin",
    "bitcoin có giá trị không": "bitcoin",
    "tại sao bitcoin có giá trị": "bitcoin",
    "bitcoin cơ bản": "bitcoin",
    "bitcoin là tiền gì": "bitcoin",
    "bitcoin có nghĩa là gì": "bitcoin",
    # Thị trường bitcoin
    "thị trường bitcoin": "bitcoin_market",
    "thị trường bitcoin là gì": "bitcoin_market",
    "thị trường btc": "bitcoin_market",
    "giao dịch bitcoin": "bitcoin_market",
    "mua bán bitcoin": "bitcoin_market",
    # Giá bitcoin
    "giá bitcoin": "bitcoin_price",
    "giá btc": "bitcoin_price",
    "giá bitcoin bao nhiêu": "bitcoin_price",
    "bitcoin giá bao nhiêu": "bitcoin_price",
    "giá bitcoin hôm nay": "bitcoin_price",
    "bitcoin trị giá bao nhiêu": "bitcoin_price",
    "tại sao giá bitcoin thay đổi": "bitcoin_price",
    "biến động giá bitcoin": "bitcoin_price",
    "lịch sử giá bitcoin": "bitcoin_price",
    # Ví bitcoin
    "ví bitcoin": "bitcoin_wallet",
    "ví bitcoin là gì": "bitcoin_wallet",
    "làm sao lưu bitcoin": "bitcoin_wallet",
    "bảo quản bitcoin": "bitcoin_wallet",
    # Khai thác
    "khai thác bitcoin": "bitcoin_mining",
    "khai thác": "bitcoin_mining",
    "mining bitcoin": "bitcoin_mining",
    "đào bitcoin": "bitcoin_mining",
    "bitcoin khai thác": "bitcoin_mining",
    "đào coin": "bitcoin_mining",
    "khai thác coin": "bitcoin_mining",
    "đào bitcoin có lời không": "bitcoin_mining",
    # Blockchain
    "blockchain": "blockchain",
    "blockchain là gì": "blockchain",
    "chuỗi khối": "blockchain",
    "chuỗi khối là gì": "blockchain",
    "công nghệ blockchain": "blockchain",
    "bitcoin blockchain": "bitcoin_blockchain",
    # Halving
    "halving": "halving",
    "halving là gì": "halving",
    "halving bitcoin": "halving",
    "bitcoin halving là gì": "halving",
    "halving ảnh hưởng giá không": "halving",
    "halving tiếp theo": "halving",
    # Phi tập trung
    "phi tập trung": "decentralization",
    "phi tập trung là gì": "decentralization",
    "decentralized là gì": "decentralization",
    "bitcoin phi tập trung": "decentralization",
    # Smart contract
    "smart contract": "smart_contract",
    "smart contracts": "smart_contract",
    "smart contract là gì": "smart_contract",
    "hợp đồng thông minh": "smart_contract",
    "hợp đồng thông minh là gì": "smart_contract",
    # DeFi
    "defi": "defi",
    "tài chính phi tập trung": "defi",
    "defi là gì": "defi",
    "tài chính phi tập trung là gì": "defi",
    # Ethereum
    "ethereum": "ethereum",
    "ethereum là gì": "ethereum",
    "eth là gì": "ethereum",
    "ethereum vs bitcoin": "ethereum",
    "ethereum khác bitcoin thế nào": "ethereum",
    # Altcoin
    "altcoin": "altcoin",
    "altcoin là gì": "altcoin",
    "coin khác bitcoin": "altcoin",
    "các coin khác": "altcoin",
    # Ví
    "ví": "wallet",
    "ví tiền điện tử": "wallet",
    "ví là gì": "wallet",
    "wallet": "wallet",
    "ví crypto": "wallet",
    "ví nóng ví lạnh": "wallet",
    # Sàn giao dịch
    "sàn giao dịch": "exchange",
    "sàn": "exchange",
    "sàn giao dịch là gì": "exchange",
    "exchange": "exchange",
    "sàn crypto": "exchange",
    "binance là gì": "exchange",
    "mua coin ở đâu": "exchange",
    # Biến động
    "biến động": "volatility",
    "volatility": "volatility",
    "biến động giá": "volatility",
    "tại sao crypto biến động nhiều": "volatility",
    "crypto rủi ro không": "volatility",
    # Thị trường crypto chung
    "thị trường là gì": "crypto_market",
    "thị trường": "crypto_market",
    "thị trường crypto": "crypto_market",
    "thị trường crypto là gì": "crypto_market",
    "thị trường tiền điện tử": "crypto_market",
    "thị trường tiền điện tử là gì": "crypto_market",
    "thị trường coin": "crypto_market",
    "thị trường coin là gì": "crypto_market",
    "crypto market là gì": "crypto_market",
    # Thị trường bò / gấu
    "thị trường bò": "bull_market",
    "bull market": "bull_market",
    "thị trường bò là gì": "bull_market",
    "uptrend": "bull_market",
    "tăng giá": "bull_market",
    "thị trường gấu": "bear_market",
    "bear market": "bear_market",
    "thị trường gấu là gì": "bear_market",
    "downtrend": "bear_market",
    "giảm giá": "bear_market",
    # Tiền điện tử
    "tiền điện tử": "cryptocurrency",
    "cryptocurrency": "cryptocurrency",
    "tiền điện tử là gì": "cryptocurrency",
    "crypto là gì": "cryptocurrency",
    "coin là gì": "cryptocurrency",
    # ─── Vietnamese: New concepts ─────────────────────────────────────────────
    # DCA
    "dca": "dca",
    "dca là gì": "dca",
    "mua đều đặn": "dca",
    "mua theo kỳ hạn": "dca",
    "đầu tư đều đặn": "dca",
    "dollar cost averaging": "dca",
    "chiến lược dca": "dca",
    "mua giá trung bình": "dca",
    "dca coin": "dca",
    # HODL
    "hodl": "hodl",
    "hodl là gì": "hodl",
    "nên giữ coin không": "hodl",
    "giữ bitcoin lâu dài": "hodl",
    "chiến lược hodl": "hodl",
    "hold coin": "hodl",
    "nắm giữ crypto": "hodl",
    "hodl hay bán": "hodl",
    # FOMO / FUD
    "fomo": "fomo_fud",
    "fud": "fomo_fud",
    "fomo là gì": "fomo_fud",
    "fud là gì": "fomo_fud",
    "sợ bỏ lỡ": "fomo_fud",
    "tâm lý fomo": "fomo_fud",
    "tin tức xấu crypto": "fomo_fud",
    "fomo fud": "fomo_fud",
    # ATH / ATL
    "ath": "ath_atl",
    "atl": "ath_atl",
    "ath là gì": "ath_atl",
    "all time high": "ath_atl",
    "đỉnh giá bitcoin": "ath_atl",
    "giá cao nhất lịch sử bitcoin": "ath_atl",
    "btc ath": "ath_atl",
    "đáy giá bitcoin": "ath_atl",
    # Staking
    "staking": "staking",
    "staking là gì": "staking",
    "stake coin": "staking",
    "kiếm lời từ staking": "staking",
    "proof of stake là gì": "staking",
    "pos là gì": "staking",
    "stake ethereum": "staking",
    "lãi suất staking": "staking",
    # NFT
    "nft": "nft",
    "nft là gì": "nft",
    "token không thể thay thế": "nft",
    "non-fungible token": "nft",
    "mua bán nft": "nft",
    "nghệ thuật kỹ thuật số": "nft",
    # Layer 2
    "layer 2": "layer2",
    "layer2": "layer2",
    "lightning network": "layer2",
    "lightning network là gì": "layer2",
    "mạng lightning": "layer2",
    "layer 2 là gì": "layer2",
    # Phí gas
    "gas fee": "gas_fee",
    "phí gas": "gas_fee",
    "gas fee là gì": "gas_fee",
    "phí giao dịch ethereum": "gas_fee",
    "phí chuyển tiền crypto": "gas_fee",
    "tại sao phí ethereum cao": "gas_fee",
    "phí network": "gas_fee",
    # Vốn hóa thị trường
    "market cap": "market_cap",
    "vốn hóa thị trường": "market_cap",
    "market cap là gì": "market_cap",
    "vốn hóa bitcoin": "market_cap",
    "tổng vốn hóa crypto": "market_cap",
    "market capitalization": "market_cap",
    "circulating supply là gì": "market_cap",
    # Cá voi
    "whale": "whale",
    "cá voi": "whale",
    "whale là gì": "whale",
    "cá voi crypto": "whale",
    "cá voi bitcoin": "whale",
    "cá voi thao túng giá": "whale",
    "holder lớn": "whale",
    # Đòn bẩy
    "leverage": "leverage",
    "đòn bẩy": "leverage",
    "leverage là gì": "leverage",
    "đòn bẩy crypto": "leverage",
    "giao dịch ký quỹ": "leverage",
    "margin trading": "leverage",
    "liquidation là gì": "leverage",
    "thanh lý vị thế": "leverage",
    "long short là gì": "leverage",
    "futures bitcoin": "leverage",
    # Whitepaper
    "whitepaper": "whitepaper",
    "whitepaper là gì": "whitepaper",
    "bitcoin whitepaper": "whitepaper",
    "whitepaper satoshi": "whitepaper",
    "sách trắng bitcoin": "whitepaper",
}

CRYPTO_BASICS_EN = {
    "bitcoin": {
        "simple": "Bitcoin is digital money, like electronic cash. Instead of banks managing it, a network of computers around the world keeps track of all Bitcoin transactions.",
        "analogy": "Think of Bitcoin like digital gold - it's limited in supply and hard to create, which makes it valuable.",
        "key_points": [
            "Created in 2009 by someone called Satoshi Nakamoto",
            "Only 21 million Bitcoin will ever exist",
            "Transactions are permanent and transparent",
            "No government or bank controls Bitcoin"
        ],
        "for_beginners": "Bitcoin is the first cryptocurrency. It's a new type of money that works without banks. You can send Bitcoin to anyone in the world, and the transaction is recorded permanently."
    },

    "bitcoin_market": {
        "simple": "The Bitcoin market is a global market where Bitcoin is bought and sold 24/7. It's worth over $1 trillion and is accessible to anyone with internet.",
        "analogy": "Like a stock market for Bitcoin - buyers and sellers come together, and the price changes based on supply and demand. Unlike stock markets, it never closes.",
        "key_points": [
            "Available 24/7/365 - no closing hours",
            "Market cap over $1 trillion USD",
            "Most Bitcoin trading happens on cryptocurrency exchanges",
            "Price is determined by millions of buyers and sellers globally"
        ],
        "for_beginners": "The Bitcoin market is where people buy and sell Bitcoin. Millions of transactions happen every day. The price constantly changes based on how many people want to buy vs. sell."
    },

    "bitcoin_price": {
        "simple": "Bitcoin's price is determined by supply and demand - how much people want to buy versus how many sellers there are. Price has ranged from $0.003 to over $69,000.",
        "analogy": "Like a stock price, Bitcoin's price goes up when demand increases and down when people want to sell. News can dramatically affect price overnight.",
        "key_points": [
            "Price set by global markets (not controlled by any single exchange)",
            "Driven by adoption, regulation, economy, and market sentiment",
            "Can swing thousands of dollars in a single day",
            "Historically: $0.003 (2010) → $69,000 (2021)"
        ],
        "for_beginners": "Bitcoin's price changes constantly based on how many people want to buy it. Big news can make the price jump or drop. Price history shows Bitcoin went from nearly worthless to tens of thousands."
    },

    "bitcoin_wallet": {
        "simple": "A Bitcoin wallet is software or hardware that stores your Bitcoin. It contains a public address (where others send you Bitcoin) and a private key (your secret password).",
        "analogy": "A Bitcoin wallet is like a bank account. Your public address is your account number (safe to share). Your private key is like your PIN - never share it with anyone.",
        "key_points": [
            "Hot wallets: online (easy but less secure)",
            "Cold wallets: offline devices (secure but less convenient)",
            "Public address: where people send you Bitcoin",
            "Private key: controls your Bitcoin - lose it and you lose your Bitcoin forever"
        ],
        "for_beginners": "A wallet stores your Bitcoin. Think of it like a digital purse. Popular wallets: MetaMask, Ledger, Trust Wallet. Always backup your private key and never share it."
    },

    "bitcoin_mining": {
        "simple": "Bitcoin mining is the process where computers solve complex math problems to verify Bitcoin transactions and add them to the blockchain. Miners are rewarded with new Bitcoin.",
        "analogy": "Like gold mining - miners work hard to extract gold from the earth. Bitcoin miners work hard (computationally) to 'extract' new Bitcoin from the network.",
        "key_points": [
            "Mining difficulty increases as more miners join",
            "Current reward: 6.25 Bitcoin per block (was 50 in 2009)",
            "Requires expensive equipment: ASIC miners cost thousands of dollars",
            "Mining is only profitable in countries with cheap electricity"
        ],
        "for_beginners": "Mining is how new Bitcoin are created and transactions are verified. Miners use computers to solve math problems and earn Bitcoin as a reward. It's becoming more expensive as the network grows."
    },

    "bitcoin_blockchain": {
        "simple": "Bitcoin's blockchain is a record of all Bitcoin transactions since 2009. It's about 500GB in size and is maintained by thousands of computers worldwide.",
        "analogy": "Imagine a history book that records every Bitcoin transaction ever made. Everyone keeps a copy of this book, so no one can fake transactions.",
        "key_points": [
            "Complete transaction history since January 2009",
            "Size: approximately 500GB (and growing)",
            "New blocks added approximately every 10 minutes",
            "Immutable: once recorded, cannot be changed"
        ],
        "for_beginners": "Bitcoin blockchain is a permanent record of all Bitcoin transfers. It's like a ledger in a bank, but everyone has a copy, making it impossible to hack or cheat."
    },

    "halving": {
        "simple": "Halving is when the Bitcoin mining reward is cut in half. It happens every 4 years (every 210,000 blocks). Started at 50 BTC, now at 6.25 BTC.",
        "analogy": "Imagine if your salary was cut in half every 4 years - that's what happens to miners. This makes Bitcoin scarcer, which historically has increased the price.",
        "key_points": [
            "Happens every 4 years / 210,000 blocks",
            "Mining rewards: 50 → 25 → 12.5 → 6.25 → 3.125 BTC",
            "Most recent halving: May 2020",
            "Next halving: April 2024 (approximately)"
        ],
        "for_beginners": "Halving is when Bitcoin mining rewards get cut in half every 4 years. This makes Bitcoin scarcer over time, which is why some people think Bitcoin's price goes up after halvings."
    },

    "decentralization": {
        "simple": "Decentralization means Bitcoin is not controlled by any single person, company, or government. Instead, thousands of computers work together to run the network.",
        "analogy": "Instead of one CEO making all decisions for a company, imagine 10,000 people voting on every decision. Bitcoin works like this - no single entity has control.",
        "key_points": [
            "No central authority needed",
            "Cannot be censored or shut down",
            "Requires network consensus for major changes",
            "More secure but slower than centralized systems"
        ],
        "for_beginners": "Bitcoin is decentralized - nobody owns it or controls it. Not your bank, not the government, not any corporation. This is why Bitcoin is trustworthy - impossible to hack or censor the entire network."
    },

    "smart_contract": {
        "simple": "A smart contract is a program that automatically executes when certain conditions are met. It runs on blockchain (like Ethereum) without needing a middleman.",
        "analogy": "Like a vending machine - you insert coins (condition met), and it automatically gives you a drink (execution). No human needs to approve or stop it.",
        "key_points": [
            "Runs on blockchain (Ethereum, Cardano, etc.)",
            "Cannot be faked, stopped, or censored",
            "Executes automatically when conditions are met",
            "Powers DeFi apps: lending, trading, insurance"
        ],
        "for_beginners": "Smart contracts are like self-executing agreements written in code. You can make loans, bets, or exchanges that happen automatically without a middleman. Ethereum lets you create smart contracts."
    },

    "defi": {
        "simple": "DeFi (Decentralized Finance) is financial services built on blockchain without banks or brokers. You can lend, borrow, and trade cryptos directly peer-to-peer.",
        "analogy": "Instead of going to a bank for a loan, you go to a DApp (app on blockchain). The agreement is executed by code, not by a banker, and happens instantly.",
        "key_points": [
            "No banks, no brokers, no middlemen",
            "Available 24/7 (no closing hours)",
            "Generally lower fees than traditional finance",
            "Higher risk - scams are common in DeFi"
        ],
        "for_beginners": "DeFi is like banking but on blockchain. You can lend crypto and earn interest, borrow crypto by providing collateral, or trade without a broker. It's transparent and trustless."
    },

    "blockchain": {
        "simple": "Blockchain is a list of records (called blocks) linked together in a chain. Each block contains transaction information and a special code linking to the previous block.",
        "analogy": "Imagine a notebook that multiple people share. When someone writes a transaction, everyone gets a copy. If someone tries to cheat and change an old transaction, everyone knows because their copies don't match.",
        "key_points": [
            "Immutable (can't be changed once written)",
            "Transparent (everyone can see transactions)",
            "Decentralized (no single person controls it)",
            "Secure (protected by cryptography)"
        ],
        "for_beginners": "Blockchain is like a ledger that records all transactions. Many computers keep copies of this ledger, making it impossible to fake or lose records."
    },

    "crypto_market": {
        "simple": "The crypto market is the global marketplace where cryptocurrencies like Bitcoin, Ethereum, and thousands of other coins are bought and sold 24/7.",
        "analogy": "Think of it like a stock market, but for digital currencies. Unlike stock markets that close at night and on weekends, the crypto market never sleeps - it runs 24 hours a day, 365 days a year.",
        "key_points": [
            "Open 24/7/365 - no closing hours, holidays, or weekends off",
            "Total market cap exceeds $2 trillion USD",
            "Thousands of cryptocurrencies are traded on hundreds of exchanges",
            "Highly volatile - prices can swing 10-30% in a single day"
        ],
        "for_beginners": "The crypto market is where people buy and sell digital currencies. It works like the stock market but never closes. Prices change based on supply and demand - when more people want to buy, prices go up; when more want to sell, prices go down."
    },

    "cryptocurrency": {
        "simple": "Cryptocurrency is digital money created using cryptography (special math codes). It operates independently of banks and governments.",
        "analogy": "Like regular money, you can send and receive cryptocurrency. But instead of physical coins/bills, it's all digital, and no bank is needed.",
        "key_points": [
            "Digital and decentralized",
            "Secured by cryptography",
            "Can be sent globally instantly",
            "Prices fluctuate based on supply/demand"
        ],
        "for_beginners": "Cryptocurrency is digital money. The most famous is Bitcoin. Each cryptocurrency has its own blockchain and purpose."
    },

    "ethereum": {
        "simple": "Ethereum is a blockchain platform that allows programmers to build applications (called DApps) on top of it. It has its own currency called Ether (ETH).",
        "analogy": "If Bitcoin is digital money, Ethereum is like a computer everyone shares. You can run programs on it and create new applications.",
        "key_points": [
            "Created in 2015 by Vitalik Buterin",
            "Enables smart contracts (self-executing agreements)",
            "More flexible than Bitcoin",
            "Powers most DeFi (decentralized finance) apps"
        ],
        "for_beginners": "Ethereum is a blockchain that's like a computer platform. Bitcoin is just money, but Ethereum can do more things - people build apps on it."
    },
    "altcoin": {
        "simple": "Altcoin means 'alternative coin' - any cryptocurrency that's not Bitcoin.",
        "analogy": "Bitcoin is the original. Altcoins are like different apps running on different platforms.",
        "key_points": [
            "Thousands of altcoins exist",
            "Each has different features/purposes",
            "More volatile than Bitcoin",
            "Can have higher risk and higher reward"
        ],
        "for_beginners": "Altcoins are cryptocurrencies other than Bitcoin. They might have different features or purposes."
    },
    "wallet": {
        "simple": "A crypto wallet is like a digital safe that holds your private and public keys. Your public key is like an account number others see, and your private key is like a password you keep secret.",
        "analogy": "A Bitcoin address is like an email address (anyone can see it), but your private key is like your email password (only you should know it).",
        "key_points": [
            "Public key: what you share to receive crypto",
            "Private key: secret code to access your crypto",
            "Never share your private key",
            "Always backup your wallet"
        ],
        "for_beginners": "A wallet stores your cryptocurrency. Think of it like a digital purse. Your public address is where others can send you crypto. Your private key is the password only you should know."
    },
    "exchange": {
        "simple": "A crypto exchange is a website where you can buy/sell cryptocurrencies using real money (like USD or EUR).",
        "analogy": "Like a bank where you exchange dollars for euros, a crypto exchange lets you exchange normal money for cryptocurrency.",
        "key_points": [
            "Centralized exchanges (like Binance, Coinbase) are easiest for beginners",
            "Decentralized exchanges (DEX) don't require personal info",
            "Fees vary by exchange",
            "Security varies - use reputable exchanges"
        ],
        "for_beginners": "An exchange is where you buy and sell crypto. Like how you exchange money at an airport, you exchange regular money for crypto on an exchange."
    },
    "volatility": {
        "simple": "Volatility means how much the price changes. High volatility = big price swings (risky). Low volatility = small price changes (safer).",
        "analogy": "Bitcoin is like a roller coaster - prices go up and down rapidly. Stablecoins are like an elevator - they stay at one level.",
        "key_points": [
            "Bitcoin is very volatile",
            "Stablecoins have low volatility",
            "Higher volatility = more risk AND more profit potential",
            "Never invest money you can't afford to lose"
        ],
        "for_beginners": "Volatility means price changes. Crypto prices change quickly, sometimes up, sometimes down. This is why it's risky."
    },
    "bear_market": {
        "simple": "A bear market is when prices fall and there's negative sentiment. The opposite of a bull market.",
        "analogy": "In a bear market, bad news about crypto spreads, and everyone wants to sell. It's like panic when prices keep dropping.",
        "key_points": [
            "Prices falling long-term",
            "Negative news/sentiment",
            "People lose confidence",
            "Can last weeks/months/years"
        ],
        "for_beginners": "Bear market = prices going down. Bull market = prices going up. We're in a bull market when most coins are rising."
    },
    "bull_market": {
        "simple": "A bull market is when prices rise and there's positive sentiment. People are confident and buying more crypto.",
        "analogy": "In a bull market, good news spreads, more people want to buy, and prices keep climbing. It's exciting but can be risky if hype gets too high.",
        "key_points": [
            "Prices rising long-term",
            "Positive news/sentiment",
            "People gain confidence",
            "Can create FOMO (fear of missing out)"
        ],
        "for_beginners": "Bull market = prices going up. This happens when more people want to buy and positive news comes out."
    },

    "dca": {
        "simple": "Dollar-Cost Averaging (DCA) is an investment strategy where you invest a fixed amount at regular intervals (weekly/monthly) regardless of price, instead of investing all at once.",
        "analogy": "Like paying a monthly subscription - you buy $100 of Bitcoin every month no matter the price. When price is low, you buy more coins. When price is high, you buy fewer. Over time, this averages out your cost.",
        "key_points": [
            "Reduces impact of price volatility",
            "Removes emotional decisions from investing",
            "Works well for long-term investors",
            "Popular strategy for beginners"
        ],
        "for_beginners": "DCA means buying a fixed amount of crypto regularly instead of all at once. Example: buy $50 of Bitcoin every week. This way you don't stress about timing the market."
    },

    "hodl": {
        "simple": "HODL means holding cryptocurrency for the long term instead of selling during price dips. It originated from a 2013 typo of 'hold' but became a popular crypto strategy.",
        "analogy": "Like buying land and keeping it for 20+ years, even when economic downturns happen. HODLers believe long-term price growth outweighs short-term losses.",
        "key_points": [
            "Originated from a Bitcoin forum post typo in 2013",
            "Core belief: Bitcoin value increases over years",
            "Avoids losing money by panic selling",
            "Requires strong conviction and patience"
        ],
        "for_beginners": "HODL = Hold On for Dear Life. It means NOT selling your crypto during price drops. Many early Bitcoin holders became millionaires by HODLing through crashes."
    },

    "fomo_fud": {
        "simple": "FOMO (Fear Of Missing Out) and FUD (Fear, Uncertainty, Doubt) are emotional forces that drive crypto markets. FOMO causes panic buying; FUD causes panic selling.",
        "analogy": "FOMO: seeing everyone post about 10x gains and rushing to buy at the top. FUD: hearing a country banned crypto and selling everything in panic. Both lead to poor decisions.",
        "key_points": [
            "FOMO = buying high because you fear missing gains",
            "FUD = selling low because of scary news or rumors",
            "Both are emotionally driven - not rational decisions",
            "Experienced traders use FOMO/FUD moments to trade against the crowd"
        ],
        "for_beginners": "FOMO makes you buy when everyone is excited (usually near the top). FUD makes you sell when everyone is scared (usually near the bottom). Recognizing these emotions helps you trade better."
    },

    "ath_atl": {
        "simple": "ATH (All-Time High) is the highest price a cryptocurrency has ever reached. ATL (All-Time Low) is the lowest. Bitcoin's ATH was ~$69,000 in November 2021.",
        "analogy": "ATH is like Usain Bolt's 9.58s record - the best ever. ATL is the worst performance ever. Investors watch these levels as important price reference points.",
        "key_points": [
            "Bitcoin ATH: ~$69,000 (Nov 2021)",
            "Bitcoin ATL: ~$0.003 (2010)",
            "Breaking ATH is often a strong bullish signal",
            "ATH levels often become future support/resistance zones"
        ],
        "for_beginners": "ATH = highest price ever, ATL = lowest price ever. When Bitcoin breaks its ATH, it means it's at a new record high - this often attracts more buyers."
    },

    "staking": {
        "simple": "Staking is locking up your cryptocurrency in a blockchain network as collateral to help validate transactions. In return, you earn rewards (like interest) in that cryptocurrency.",
        "analogy": "Like putting money in a fixed deposit at a bank - you lock it for a period and earn interest. Instead of a bank, you lock crypto in a blockchain and earn more crypto.",
        "key_points": [
            "Earns passive crypto income (typically 4-15% APY)",
            "Used in Proof-of-Stake (PoS) blockchains",
            "Ethereum staking requires 32 ETH minimum",
            "Risk: locked funds can't be sold during price drops"
        ],
        "for_beginners": "Staking means locking your crypto so the network can use it to verify transactions. You earn reward coins for doing this - like earning interest from a savings account."
    },

    "nft": {
        "simple": "NFT (Non-Fungible Token) is a unique digital asset stored on a blockchain. Unlike Bitcoin (where every coin is identical), each NFT is one-of-a-kind and cannot be copied.",
        "analogy": "A dollar bill is fungible (any dollar equals any other dollar). But a signed Michael Jordan trading card is non-fungible - it's unique. NFTs are digital versions of unique collectibles.",
        "key_points": [
            "Each NFT has a unique ID on the blockchain",
            "Used for digital art, collectibles, gaming items, music",
            "Ownership is verified on blockchain (permanent proof)",
            "Market peaked in 2021-2022, then crashed significantly"
        ],
        "for_beginners": "NFTs are digital items that are one-of-a-kind. You can own a digital artwork and the blockchain proves you own it. Popular NFT collections: CryptoPunks, Bored Ape Yacht Club."
    },

    "layer2": {
        "simple": "Layer 2 (L2) is a secondary network built on top of a main blockchain (Layer 1) to improve speed and reduce transaction costs. Bitcoin's Layer 2 is the Lightning Network.",
        "analogy": "Highway (Layer 1) gets congested. The government builds an express lane on top (Layer 2) for faster traffic. You use the express lane for daily drives and the main highway for big trips.",
        "key_points": [
            "Bitcoin Lightning Network enables instant micropayments",
            "Ethereum L2s: Arbitrum, Optimism, Polygon",
            "Fees on L2 can be 100x cheaper than main chain",
            "Trades security for speed (slightly less decentralized)"
        ],
        "for_beginners": "Layer 2 makes blockchain faster and cheaper. Without L2, sending $1 of Bitcoin could cost $5 in fees. Lightning Network lets you send Bitcoin instantly for fractions of a cent."
    },

    "gas_fee": {
        "simple": "Gas fees are transaction fees paid to the Ethereum network for processing transactions. They're paid in ETH (called Gwei) and vary based on network congestion.",
        "analogy": "Like taxi base fare + surge pricing. The 'taxi' is the Ethereum network, the 'fare' is gas, and 'surge pricing' activates when many people want transactions at once.",
        "key_points": [
            "Gas = computation units needed for a transaction",
            "Gas price (Gwei) varies with network demand",
            "Complex DeFi transactions cost more gas than simple transfers",
            "Can be $1 during quiet periods or $200+ during congestion"
        ],
        "for_beginners": "Gas fees are the price you pay to use the Ethereum network. Sending ETH or using a DeFi app costs gas. Fees are cheap at night (low traffic) and expensive during busy periods."
    },

    "market_cap": {
        "simple": "Market cap = current price × total circulating supply. It represents the total market value of a cryptocurrency. Bitcoin's market cap is ~$1 trillion, representing ~50% of all crypto.",
        "analogy": "A company with $100/share and 1 million shares has a $100 million market cap. Bitcoin at $65,000 with 19.5 million coins = ~$1.27 trillion market cap.",
        "key_points": [
            "Formula: Price × Circulating Supply",
            "Bitcoin dominance = BTC market cap / all crypto market cap",
            "Larger market cap = more established, less volatile",
            "Small-cap coins are riskier but have higher growth potential"
        ],
        "for_beginners": "Market cap tells you the total value of a cryptocurrency. Bitcoin has the biggest market cap in crypto. A coin with high market cap is generally safer than a coin with very low market cap."
    },

    "whale": {
        "simple": "A crypto whale is an individual or entity holding a very large amount of cryptocurrency - enough to influence market prices when they buy or sell.",
        "analogy": "Imagine an ocean where small fish are ordinary investors. Whales are so big that when they swim, they create waves that move all the small fish. Bitcoin whales can move the market.",
        "key_points": [
            "No official definition, but typically holds 1,000+ BTC",
            "Whale movements tracked on public blockchain",
            "Large buys/sells can cause price swings for others",
            "Some whales: Satoshi Nakamoto (~1M BTC), Grayscale, MicroStrategy"
        ],
        "for_beginners": "Whales are crypto holders with so much coin that when they buy or sell, it moves the entire market. When a whale sells Bitcoin, prices can drop fast. Traders watch 'whale wallets' for signals."
    },

    "leverage": {
        "simple": "Leverage trading lets you control a position larger than your actual funds. With 10x leverage, $100 controls a $1,000 position - amplifying both profits and losses.",
        "analogy": "Using a 10x lever to lift a car: small effort, big result. But if you slip, the car falls on you. Leverage amplifies gains but can wipe out your entire investment instantly.",
        "key_points": [
            "Common leverage ratios: 2x, 5x, 10x, 20x, 100x",
            "Liquidation: position is forcibly closed if you lose too much",
            "Highly risky - 80%+ of leverage traders lose money",
            "Available on Binance Futures, BitMEX, Bybit"
        ],
        "for_beginners": "Leverage lets you trade with more money than you have. With 10x leverage, a 10% price move wipes out your entire investment. Beginners should NEVER use leverage."
    },

    "whitepaper": {
        "simple": "A whitepaper is a technical document that explains how a cryptocurrency works - its technology, purpose, and how it solves a problem. Bitcoin's whitepaper by Satoshi Nakamoto was published Oct 31, 2008.",
        "analogy": "Like a business plan for a cryptocurrency. It explains the 'why' (what problem it solves) and 'how' (the technical solution). Reading a whitepaper helps you judge if a project is legitimate.",
        "key_points": [
            "Bitcoin whitepaper title: 'Bitcoin: A Peer-to-Peer Electronic Cash System'",
            "Published on October 31, 2008 by Satoshi Nakamoto",
            "Only 9 pages long - one of the most influential documents in tech history",
            "Most crypto scams have no whitepaper or copy others"
        ],
        "for_beginners": "The Bitcoin whitepaper is the original document that explained Bitcoin to the world. Before investing in any crypto, check if it has a whitepaper. No whitepaper = likely a scam."
    },
}

CRYPTO_BASICS_VI = {
    "bitcoin": {
        "simple": "Bitcoin là tiền kỹ thuật số, giống như tiền mặt điện tử. Thay vì ngân hàng quản lý, một mạng lưới máy tính trên toàn thế giới theo dõi tất cả các giao dịch Bitcoin.",
        "analogy": "Hãy nghĩ Bitcoin như vàng kỹ thuật số - nó có cung cấp hạn chế và khó tạo ra, điều này làm cho nó có giá trị.",
        "key_points": [
            "Được tạo ra năm 2009 bởi Satoshi Nakamoto",
            "Chỉ có 21 triệu Bitcoin sẽ tồn tại",
            "Giao dịch là vĩnh viễn và minh bạch",
            "Không có chính phủ hay ngân hàng nào kiểm soát Bitcoin"
        ],
        "for_beginners": "Bitcoin là tiền điện tử đầu tiên. Đó là loại tiền mới hoạt động mà không cần ngân hàng. Bạn có thể gửi Bitcoin cho bất kỳ ai trên thế giới, và giao dịch được ghi lại vĩnh viễn."
    },
    "blockchain": {
        "simple": "Blockchain là một danh sách các bản ghi (gọi là blocks) được liên kết với nhau thành một chuỗi. Mỗi block chứa thông tin giao dịch và một mã đặc biệt liên kết đến block trước đó.",
        "analogy": "Hãy tưởng tượng một cuốn sổ mà nhiều người chia sẻ. Khi ai đó ghi một giao dịch, mọi người đều nhận được bản sao. Nếu ai đó cố gắng gian lận và thay đổi một giao dịch cũ, mọi người sẽ biết vì bản sao của họ không trùng khớp.",
        "key_points": [
            "Bất biến (không thể thay đổi sau khi viết)",
            "Minh bạch (mọi người có thể thấy giao dịch)",
            "Phi tập trung (không có người nào kiểm soát)",
            "An toàn (được bảo vệ bằng mã hóa)"
        ],
        "for_beginners": "Blockchain giống như một ledger ghi lại tất cả các giao dịch. Nhiều máy tính lưu giữ bản sao của ledger này, làm cho việc giả mạo hoặc mất bản ghi là điều không thể."
    },
    "cryptocurrency": {
        "simple": "Tiền điện tử là tiền kỹ thuật số được tạo ra bằng mã hóa (các mã toán đặc biệt). Nó hoạt động độc lập với ngân hàng và chính phủ.",
        "analogy": "Giống như tiền thông thường, bạn có thể gửi và nhận tiền điện tử. Nhưng thay vì xu vàng/tờ tiền vật lý, tất cả đều kỹ thuật số, và không cần ngân hàng.",
        "key_points": [
            "Kỹ thuật số và phi tập trung",
            "Được bảo vệ bằng mã hóa",
            "Có thể gửi toàn cầu tức thì",
            "Giá dao động dựa trên cung/cầu"
        ],
        "for_beginners": "Tiền điện tử là tiền kỹ thuật số. Nổi tiếng nhất là Bitcoin. Mỗi tiền điện tử có blockchain và mục đích riêng của nó."
    },
    "ethereum": {
        "simple": "Ethereum là một nền tảng blockchain cho phép các lập trình viên xây dựng các ứng dụng (gọi là DApps) trên nó. Nó có tiền tệ riêng gọi là Ether (ETH).",
        "analogy": "Nếu Bitcoin là tiền kỹ thuật số, Ethereum giống như một máy tính mà mọi người chia sẻ. Bạn có thể chạy các chương trình trên nó và tạo các ứng dụng mới.",
        "key_points": [
            "Được tạo ra năm 2015 bởi Vitalik Buterin",
            "Cho phép smart contracts (các thỏa thuận tự thực hiện)",
            "Linh hoạt hơn Bitcoin",
            "Cung cấp năng lượng cho hầu hết các ứng dụng DeFi"
        ],
        "for_beginners": "Ethereum là một blockchain giống như một nền tảng máy tính. Bitcoin chỉ là tiền, nhưng Ethereum có thể làm nhiều thứ hơn - mọi người xây dựng các ứng dụng trên nó."
    },
    "altcoin": {
        "simple": "Altcoin có nghĩa là 'tiền thay thế' - bất kỳ tiền điện tử nào không phải Bitcoin.",
        "analogy": "Bitcoin là bản gốc. Altcoins giống như các ứng dụng khác nhau chạy trên các nền tảng khác nhau.",
        "key_points": [
            "Hàng nghìn altcoins tồn tại",
            "Mỗi cái có các tính năng/mục đích khác nhau",
            "Biến động hơn Bitcoin",
            "Có thể có rủi ro cao hơn và phần thưởng cao hơn"
        ],
        "for_beginners": "Altcoins là các tiền điện tử không phải Bitcoin. Chúng có thể có các tính năng hoặc mục đích khác nhau."
    },
    "wallet": {
        "simple": "Ví tiền điện tử giống như một két sắt kỹ thuật số chứa các khóa công khai và riêng của bạn. Khóa công khai của bạn giống như số tài khoản mà người khác nhìn thấy, và khóa riêng của bạn giống như mật khẩu bạn giữ bí mật.",
        "analogy": "Địa chỉ Bitcoin giống như địa chỉ email (bất kỳ ai cũng có thể thấy), nhưng khóa riêng của bạn giống như mật khẩu email của bạn (chỉ bạn mới nên biết).",
        "key_points": [
            "Khóa công khai: cái bạn chia sẻ để nhận tiền điện tử",
            "Khóa riêng: mã bí mật để truy cập tiền điện tử của bạn",
            "Không bao giờ chia sẻ khóa riêng của bạn",
            "Luôn sao lưu ví của bạn"
        ],
        "for_beginners": "Ví lưu trữ tiền điện tử của bạn. Hãy coi nó giống như một chiếc ví kỹ thuật số. Địa chỉ công khai của bạn là nơi người khác có thể gửi tiền điện tử cho bạn. Khóa riêng của bạn là mật khẩu chỉ bạn nên biết."
    },
    "exchange": {
        "simple": "Sàn giao dịch tiền điện tử là một trang web nơi bạn có thể mua/bán tiền điện tử bằng tiền thực tế (như USD hoặc EUR).",
        "analogy": "Giống như một ngân hàng nơi bạn đổi đô la lấy euro, sàn giao dịch tiền điện tử cho phép bạn đổi tiền thông thường lấy tiền điện tử.",
        "key_points": [
            "Sàn giao dịch tập trung (như Binance, Coinbase) dễ nhất cho người mới bắt đầu",
            "Sàn giao dịch phi tập trung (DEX) không yêu cầu thông tin cá nhân",
            "Phí khác nhau tùy theo sàn",
            "Bảo mật khác nhau - sử dụng các sàn có uy tín"
        ],
        "for_beginners": "Sàn giao dịch là nơi bạn mua và bán tiền điện tử. Giống như cách bạn đổi tiền ở sân bay, bạn đổi tiền thông thường lấy tiền điện tử trên sàn giao dịch."
    },
    "volatility": {
        "simple": "Biến động có nghĩa là giá thay đổi bao nhiêu. Biến động cao = sự thay đổi giá lớn (rủi ro). Biến động thấp = thay đổi giá nhỏ (an toàn hơn).",
        "analogy": "Bitcoin giống như một tàu lượn siêu tốc - giá tăng và giảm nhanh chóng. Stablecoins giống như một chiếc thang máy - chúng ở cùng một mức.",
        "key_points": [
            "Bitcoin rất biến động",
            "Stablecoins có biến động thấp",
            "Biến động cao hơn = rủi ro cao hơn VÀ lợi nhuận cao hơn",
            "Không bao giờ đầu tư tiền bạn không thể mất"
        ],
        "for_beginners": "Biến động có nghĩa là thay đổi giá. Giá tiền điện tử thay đổi nhanh chóng, đôi khi tăng, đôi khi giảm. Đó là lý do tại sao nó rủi ro."
    },
    "bear_market": {
        "simple": "Thị trường gấu là khi giá giảm và có tinh thần tiêu cực. Ngược lại với thị trường bò.",
        "analogy": "Trong thị trường gấu, tin tức xấu về tiền điện tử lan truyền, và mọi người muốn bán. Giống như hoảng loạn khi giá liên tục giảm.",
        "key_points": [
            "Giá giảm dài hạn",
            "Tin tức/tinh thần tiêu cực",
            "Mọi người mất niềm tin",
            "Có thể kéo dài hàng tuần/tháng/năm"
        ],
        "for_beginners": "Thị trường gấu = giá đi xuống. Thị trường bò = giá đi lên. Chúng ta ở trong thị trường bò khi hầu hết các coin đang tăng."
    },
    "bull_market": {
        "simple": "Thị trường bò là khi giá tăng và có tinh thần tích cực. Mọi người có tự tin và mua thêm tiền điện tử.",
        "analogy": "Trong thị trường bò, tin tức tốt lan truyền, nhiều người muốn mua, và giá tiếp tục tăng. Nó rất thú vị nhưng có thể rủi ro nếu hype trở nên quá cao.",
        "key_points": [
            "Giá tăng dài hạn",
            "Tin tức/tinh thần tích cực",
            "Mọi người đạt được sự tự tin",
            "Có thể tạo ra FOMO (sợ bỏ lỡ)"
        ],
        "for_beginners": "Thị trường bò = giá đi lên. Điều này xảy ra khi nhiều người muốn mua và tin tức tích cực xuất hiện."
    },

    "crypto_market": {
        "simple": "Thị trường crypto (thị trường tiền điện tử) là nơi mua bán các đồng tiền số như Bitcoin, Ethereum và hàng nghìn coin khác, hoạt động 24/7 trên toàn cầu.",
        "analogy": "Giống như thị trường chứng khoán nhưng dành cho tiền điện tử. Khác với chứng khoán đóng cửa cuối tuần, thị trường crypto chạy 24 giờ mỗi ngày, 365 ngày mỗi năm, không bao giờ nghỉ.",
        "key_points": [
            "Mở cửa 24/7/365 - không có giờ đóng cửa hay ngày nghỉ",
            "Tổng vốn hóa thị trường vượt 2 nghìn tỷ USD",
            "Hàng nghìn đồng coin được giao dịch trên hàng trăm sàn",
            "Biến động cao - giá có thể thay đổi 10-30% trong một ngày"
        ],
        "for_beginners": "Thị trường crypto là nơi mọi người mua và bán tiền điện tử. Nó hoạt động giống thị trường chứng khoán nhưng không bao giờ đóng cửa. Giá thay đổi dựa trên cung cầu - nhiều người muốn mua thì giá tăng, nhiều người muốn bán thì giá giảm."
    },

    "bitcoin_market": {
        "simple": "Thị trường Bitcoin là thị trường toàn cầu nơi Bitcoin được mua bán 24/7. Nó có giá trị hơn 1 nghìn tỷ đô la và có thể truy cập bởi bất kỳ ai có internet.",
        "analogy": "Giống như thị trường chứng khoán cho Bitcoin - người mua và bán gặp nhau, và giá thay đổi dựa trên cung và cầu. Không giống thị trường chứng khoán, nó không bao giờ đóng cửa.",
        "key_points": [
            "Có sẵn 24/7/365 - không có giờ đóng cửa",
            "Vốn hóa thị trường hơn 1 nghìn tỷ đô la USD",
            "Hầu hết giao dịch Bitcoin xảy ra trên các sàn giao dịch tiền điện tử",
            "Giá được xác định bởi hàng triệu người mua và bán trên toàn cầu"
        ],
        "for_beginners": "Thị trường Bitcoin là nơi mọi người mua và bán Bitcoin. Hàng triệu giao dịch xảy ra mỗi ngày. Giá liên tục thay đổi dựa trên số lượng người muốn mua so với bán."
    },

    "bitcoin_price": {
        "simple": "Giá Bitcoin được xác định bởi cung và cầu - mức độ mà mọi người muốn mua so với số lượng bán. Giá đã dao động từ 0,003 đô la đến hơn 69.000 đô la.",
        "analogy": "Giống như giá chứng khoán, giá Bitcoin tăng khi cầu tăng và giảm khi mọi người muốn bán. Tin tức có thể ảnh hưởng đáng kể đến giá từ đêm hôm trước.",
        "key_points": [
            "Giá được đặt bởi thị trường toàn cầu (không được kiểm soát bởi bất kỳ sàn nào)",
            "Được thúc đẩy bởi sự áp dụng, quy định, kinh tế và tâm lý thị trường",
            "Có thể dao động hàng nghìn đô la trong một ngày",
            "Lịch sử: 0,003 đô la (2010) → 69.000 đô la (2021)"
        ],
        "for_beginners": "Giá Bitcoin thay đổi liên tục dựa trên mức độ mà mọi người muốn mua nó. Tin tức lớn có thể làm giá tăng hoặc giảm. Lịch sử giá cho thấy Bitcoin đã đi từ gần như không có giá trị đến hàng chục nghìn."
    },

    "bitcoin_wallet": {
        "simple": "Ví Bitcoin là phần mềm hoặc phần cứng lưu trữ Bitcoin của bạn. Nó chứa địa chỉ công khai (nơi người khác gửi Bitcoin cho bạn) và khóa riêng (mật khẩu bí mật của bạn).",
        "analogy": "Ví Bitcoin giống như một tài khoản ngân hàng. Địa chỉ công khai của bạn là số tài khoản của bạn (an toàn để chia sẻ). Khóa riêng của bạn giống như PIN của bạn - không bao giờ chia sẻ nó với ai.",
        "key_points": [
            "Ví nóng: trực tuyến (dễ nhưng kém an toàn hơn)",
            "Ví lạnh: thiết bị ngoại tuyến (an toàn nhưng kém tiện lợi)",
            "Địa chỉ công khai: nơi mọi người gửi Bitcoin cho bạn",
            "Khóa riêng: kiểm soát Bitcoin của bạn - mất nó và bạn mất Bitcoin của bạn mãi mãi"
        ],
        "for_beginners": "Ví lưu trữ Bitcoin của bạn. Hãy coi nó giống như một ví kỹ thuật số. Các ví phổ biến: MetaMask, Ledger, Trust Wallet. Luôn sao lưu khóa riêng của bạn và không bao giờ chia sẻ nó."
    },

    "bitcoin_mining": {
        "simple": "Khai thác Bitcoin là quá trình mà các máy tính giải các bài toán phức tạp để xác minh các giao dịch Bitcoin và thêm chúng vào blockchain. Những thợ mỏ được thưởng bằng Bitcoin mới.",
        "analogy": "Giống như khai thác vàng - những thợ mỏ làm việc chăm chỉ để khai thác vàng từ đất. Người khai thác Bitcoin làm việc chăm chỉ (về mặt tính toán) để 'khai thác' Bitcoin mới từ mạng.",
        "key_points": [
            "Khó khai thác tăng khi bạo dạn nhiều thợ mỏ tham gia",
            "Phần thưởng hiện tại: 6,25 Bitcoin trên mỗi khối (là 50 vào năm 2009)",
            "Yêu cầu thiết bị đắt tiền: Máy khai thác ASIC có giá hàng nghìn đô la",
            "Khai thác chỉ có lợi nhuận ở các quốc gia có điện rẻ"
        ],
        "for_beginners": "Khai thác là cách Bitcoin mới được tạo ra và các giao dịch được xác minh. Những thợ mỏ sử dụng máy tính để giải các bài toán toán học và kiếm Bitcoin làm phần thưởng. Nó trở nên mắc hơn khi mạng phát triển."
    },

    "bitcoin_blockchain": {
        "simple": "Blockchain Bitcoin là bản ghi của tất cả các giao dịch Bitcoin kể từ năm 2009. Nó có kích thước khoảng 500GB và được duy trì bởi hàng nghìn máy tính trên toàn thế giới.",
        "analogy": "Hãy tưởng tượng một cuốn sách lịch sử ghi lại mỗi giao dịch Bitcoin từng được thực hiện. Mọi người đều lưu giữ một bản sao của cuốn sách này, vì vậy không ai có thể giả mạo giao dịch.",
        "key_points": [
            "Lịch sử giao dịch hoàn chỉnh kể từ tháng 1 năm 2009",
            "Kích thước: khoảng 500GB (và ngày càng tăng)",
            "Các khối mới được thêm vào khoảng mỗi 10 phút",
            "Bất biến: sau khi được ghi lại, không thể thay đổi"
        ],
        "for_beginners": "Blockchain Bitcoin là bản ghi vĩnh viễn của tất cả các chuyển tải Bitcoin. Nó giống như một cuốn sổ chi tiêu ở một ngân hàng, nhưng mọi người đều có một bản sao, làm cho việc hack hoặc gian lận là điều không thể."
    },

    "halving": {
        "simple": "Halving là khi phần thưởng khai thác Bitcoin được cắt giảm một nửa. Nó xảy ra mỗi 4 năm (mỗi 210.000 khối). Bắt đầu từ 50 BTC, bây giờ là 6,25 BTC.",
        "analogy": "Hãy tưởng tượng nếu lương của bạn bị cắt giảm một nửa mỗi 4 năm - đó là điều xảy ra với những thợ mỏ. Điều này làm cho Bitcoin trở nên khan hiếm hơn, về mặt lịch sử đã làm tăng giá.",
        "key_points": [
            "Xảy ra mỗi 4 năm / 210.000 khối",
            "Phần thưởng khai thác: 50 → 25 → 12,5 → 6,25 → 3,125 BTC",
            "Halving trước: Tháng 5 năm 2020 (12,5 → 6,25 BTC)",
            "Halving tiếp theo ước tính: Tháng 4 năm 2024"
        ],
        "for_beginners": "Halving là khi phần thưởng khai thác Bitcoin bị cắt giảm một nửa mỗi 4 năm. Điều này làm cho Bitcoin trở nên khan hiếm hơn theo thời gian, đó là lý do tại sao một số người nghĩ giá Bitcoin tăng sau halving."
    },

    "decentralization": {
        "simple": "Phân quyền có nghĩa là Bitcoin không được kiểm soát bởi bất kỳ cá nhân, công ty hoặc chính phủ nào. Thay vào đó, hàng nghìn máy tính làm việc cùng nhau để chạy mạng.",
        "analogy": "Thay vì một CEO đưa ra tất cả các quyết định cho một công ty, hãy tưởng tượng 10.000 người bỏ phiếu cho mỗi quyết định. Bitcoin hoạt động theo cách này - không có thực thể nào có quyền kiểm soát.",
        "key_points": [
            "Không cần cơ quan trung ương",
            "Không thể kiểm duyệt hoặc tắt",
            "Yêu cầu sự đồng thuận của mạng để thay đổi lớn",
            "An toàn hơn nhưng chậm hơn so với các hệ thống tập trung"
        ],
        "for_beginners": "Bitcoin được phân quyền - không ai sở hữu hoặc kiểm soát nó. Không phải ngân hàng của bạn, không phải chính phủ, không phải bất kỳ tập đoàn nào. Đây là lý do tại sao Bitcoin đáng tin cậy - không thể hack hoặc kiểm duyệt toàn bộ mạng."
    },

    "smart_contract": {
        "simple": "Hợp đồng thông minh là một chương trình tự động thực thi khi đáp ứng các điều kiện nhất định. Nó chạy trên blockchain (như Ethereum) mà không cần một trung gian.",
        "analogy": "Giống như một cây bán hàng tự động - bạn nhập xu (điều kiện đáp ứng) và nó tự động cho bạn một thức uống (thực thi). Không có con người nào cần phê duyệt hoặc dừng nó.",
        "key_points": [
            "Chạy trên blockchain (Ethereum, Cardano, v.v.)",
            "Không thể giả mạo, dừng hoặc kiểm duyệt",
            "Tự động thực thi khi đáp ứng các điều kiện",
            "Cung cấp năng lượng cho các ứng dụng DeFi: cho vay, giao dịch, bảo hiểm"
        ],
        "for_beginners": "Hợp đồng thông minh giống như các thỏa thuận tự thực hiện được viết bằng mã. Bạn có thể thực hiện các khoản vay, cược hoặc trao đổi xảy ra tự động mà không cần một trung gian. Ethereum cho phép bạn tạo hợp đồng thông minh."
    },

    "defi": {
        "simple": "DeFi (Tài chính Phi tập trung) là các dịch vụ tài chính được xây dựng trên blockchain mà không có ngân hàng hoặc môi giới. Bạn có thể cho vay, vay mượn và giao dịch cryptos trực tiếp peer-to-peer.",
        "analogy": "Thay vì đi đến ngân hàng để vay tiền, bạn đi đến một DApp (ứng dụng trên blockchain). Thỏa thuận được thực thi bằng mã, không phải bởi một nhân viên ngân hàng, và xảy ra tức thì.",
        "key_points": [
            "Không có ngân hàng, không có môi giới, không có trung gian",
            "Có sẵn 24/7 (không có giờ đóng cửa)",
            "Thông thường có phí thấp hơn tài chính truyền thống",
            "Rủi ro cao hơn - các lừa đảo phổ biến trong DeFi"
        ],
        "for_beginners": "DeFi giống như ngân hàng nhưng trên blockchain. Bạn có thể cho vay crypto và kiếm lãi suất, vay crypto bằng cách cung cấp tài sản thế chấp, hoặc giao dịch mà không cần môi giới. Nó minh bạch và không cần tin cậy."
    },

    "dca": {
        "simple": "Dollar-Cost Averaging (DCA) là chiến lược đầu tư mua một lượng tiền cố định theo chu kỳ đều đặn (hàng tuần/tháng) không quan tâm đến giá, thay vì mua 1 lần duy nhất.",
        "analogy": "Giống như đóng tiền điện hàng tháng - bạn mua 500 nghìn Bitcoin mỗi tháng bất kể giá nào. Khi giá rẻ, bạn mua được nhiều coin. Khi giá đắt, bạn mua ít hơn. Theo thời gian, chi phí trung bình ra.",
        "key_points": [
            "Giảm tác động của biến động giá",
            "Loại bỏ đầu tư cảm xúc (mua đỉnh, bán đáy)",
            "Phù hợp cho nhà đầu tư dài hạn",
            "Chiến lược đơn giản và hiệu quả cho người mới"
        ],
        "for_beginners": "DCA = mua đều đặn. Thay vì đổ tiền vào một lần, bạn mua một ít mỗi tuần hoặc mỗi tháng. Ví dụ: mua 200k Bitcoin mỗi tuần, không cần quan tâm giá tăng hay giảm."
    },

    "hodl": {
        "simple": "HODL là chiến lược giữ tiền điện tử dài hạn thay vì bán khi giá giảm. Bắt nguồn từ lỗi đánh máy 'hold' trên diễn đàn Bitcoin năm 2013 nhưng trở thành chiến lược phổ biến.",
        "analogy": "Như mua đất và giữ 20+ năm, kể cả khi kinh tế suy thoái. Người HODL tin rằng Bitcoin sẽ có giá trị cao hơn trong tương lai nên không bán dù giá giảm 80%.",
        "key_points": [
            "Xuất phát từ bài đăng lỗi chính tả trên forum Bitcoin 2013",
            "Niềm tin cốt lõi: Giá trị Bitcoin tăng theo năm",
            "Tránh mất tiền vì bán hoảng loạn",
            "Cần sự kiên nhẫn và niềm tin mạnh mẽ"
        ],
        "for_beginners": "HODL = giữ không bán. Nhiều người mua Bitcoin từ sớm không bán qua các đợt giảm mạnh và trở thành triệu phú. Bí quyết: mua và giữ, đừng hoảng loạn bán khi giá giảm."
    },

    "fomo_fud": {
        "simple": "FOMO (Fear Of Missing Out - Sợ Bỏ Lỡ) và FUD (Fear, Uncertainty, Doubt - Sợ hãi, Không chắc chắn, Nghi ngờ) là 2 cảm xúc thúc đẩy thị trường crypto. FOMO gây mua hoảng; FUD gây bán hoảng.",
        "analogy": "FOMO: thấy mọi người đăng lãi 10x rồi đổ tiền vào lúc đỉnh giá. FUD: nghe tin một nước cấm crypto rồi bán tháo hết. Cả hai đều dẫn đến quyết định tồi.",
        "key_points": [
            "FOMO = mua cao vì sợ bỏ lỡ cơ hội",
            "FUD = bán thấp vì sợ hãi trước tin xấu",
            "Cả hai đều là phản ứng cảm xúc, không lý trí",
            "Trader giàu kinh nghiệm giao dịch ngược lại FOMO/FUD"
        ],
        "for_beginners": "FOMO khiến bạn mua khi ai cũng hứng khởi (thường ở đỉnh). FUD khiến bạn bán khi ai cũng sợ hãi (thường ở đáy). Nhận ra 2 cảm xúc này giúp bạn đưa ra quyết định tốt hơn."
    },

    "ath_atl": {
        "simple": "ATH (All-Time High) là mức giá cao nhất lịch sử của một đồng coin. ATL (All-Time Low) là mức thấp nhất. Bitcoin đạt ATH ~69.000 USD vào tháng 11/2021.",
        "analogy": "ATH giống kỷ lục Olympic - thành tích tốt nhất từ trước đến nay. ATL là kỷ lục tệ nhất. Nhà đầu tư theo dõi 2 mức này như tham chiếu quan trọng về giá.",
        "key_points": [
            "Bitcoin ATH: ~69.000 USD (tháng 11/2021)",
            "Bitcoin ATL: ~0.003 USD (2010)",
            "Phá vỡ ATH thường là tín hiệu tăng rất mạnh",
            "Vùng ATH thường trở thành hỗ trợ/kháng cự trong tương lai"
        ],
        "for_beginners": "ATH = giá cao nhất lịch sử, ATL = giá thấp nhất lịch sử. Khi Bitcoin phá ATH nghĩa là đang lập kỷ lục mới - thường thu hút thêm nhiều người mua."
    },

    "staking": {
        "simple": "Staking là khóa tiền điện tử trong mạng blockchain để giúp xác minh giao dịch. Đổi lại, bạn nhận phần thưởng (như lãi suất) bằng đồng coin đó.",
        "analogy": "Như gửi tiết kiệm kỳ hạn ngân hàng - bạn khóa tiền trong một kỳ hạn và nhận lãi suất. Thay vì ngân hàng, bạn khóa coin vào blockchain và nhận thêm coin.",
        "key_points": [
            "Kiếm thu nhập thụ động từ crypto (thường 4-15% mỗi năm)",
            "Dùng trong các blockchain Proof-of-Stake (PoS)",
            "Staking Ethereum yêu cầu tối thiểu 32 ETH",
            "Rủi ro: tiền bị khóa không bán được khi giá giảm"
        ],
        "for_beginners": "Staking = khóa coin để mạng dùng xác minh giao dịch, đổi lại bạn nhận coin mới mỗi ngày. Giống gửi tiết kiệm nhưng với crypto. Lãi suất staking thường cao hơn ngân hàng nhiều."
    },

    "nft": {
        "simple": "NFT (Non-Fungible Token) là tài sản kỹ thuật số độc nhất được lưu trên blockchain. Không giống Bitcoin (mỗi coin như nhau), mỗi NFT là duy nhất và không thể sao chép.",
        "analogy": "Tờ 100k nào cũng như nhau (có thể thay thế). Nhưng tranh Picasso gốc là độc nhất (không thể thay thế). NFT là phiên bản kỹ thuật số của những thứ độc nhất như tranh, card, vật phẩm game.",
        "key_points": [
            "Mỗi NFT có ID duy nhất trên blockchain",
            "Dùng cho nghệ thuật số, collectibles, vật phẩm game, âm nhạc",
            "Quyền sở hữu được xác minh mãi mãi trên blockchain",
            "Thị trường NFT đạt đỉnh 2021-2022, sau đó sập mạnh"
        ],
        "for_beginners": "NFT là đồ vật kỹ thuật số độc nhất vô nhị. Bạn có thể sở hữu một bức tranh số và blockchain chứng minh bạn là chủ nhân. Các bộ sưu tập nổi tiếng: CryptoPunks, Bored Ape Yacht Club."
    },

    "layer2": {
        "simple": "Layer 2 là mạng lưới xây dựng bên trên blockchain chính (Layer 1) để tăng tốc độ và giảm phí giao dịch. Layer 2 của Bitcoin là Lightning Network.",
        "analogy": "Đường cao tốc (Layer 1) bị tắc. Chính phủ xây thêm đường cao tốc phụ bên trên (Layer 2) để đi nhanh hơn. Dùng đường phụ cho các chuyến đi hàng ngày, đường chính cho hàng hóa lớn.",
        "key_points": [
            "Lightning Network cho phép thanh toán Bitcoin tức thì",
            "Ethereum L2: Arbitrum, Optimism, Polygon",
            "Phí trên L2 rẻ hơn Layer 1 đến 100 lần",
            "Đánh đổi một chút bảo mật để đạt tốc độ cao hơn"
        ],
        "for_beginners": "Layer 2 làm blockchain nhanh hơn và rẻ hơn. Không có L2, gửi 50k Bitcoin có thể mất 200k tiền phí. Lightning Network cho phép gửi Bitcoin tức thì với phí cực rẻ."
    },

    "gas_fee": {
        "simple": "Gas fee là phí giao dịch trả cho mạng Ethereum để xử lý giao dịch. Trả bằng ETH (đơn vị Gwei) và thay đổi tùy theo mức độ tắc nghẽn của mạng.",
        "analogy": "Như cước taxi gồm phí cơ bản + phụ phí giờ cao điểm. 'Taxi' là mạng Ethereum, 'cước' là gas, 'giờ cao điểm' là lúc nhiều người dùng mạng cùng lúc.",
        "key_points": [
            "Gas = đơn vị tính toán cần thiết cho giao dịch",
            "Giá gas (Gwei) thay đổi theo nhu cầu mạng",
            "Giao dịch DeFi phức tạp tốn nhiều gas hơn chuyển tiền đơn giản",
            "Có thể 20k đêm khuya hoặc 5 triệu lúc tắc nghẽn"
        ],
        "for_beginners": "Gas fee là phí trả để dùng mạng Ethereum. Gửi ETH hoặc dùng ứng dụng DeFi đều tốn phí gas. Phí rẻ ban đêm (ít người dùng) và đắt lúc đông người. Nhiều người dùng Polygon hoặc Arbitrum để tránh phí cao."
    },

    "market_cap": {
        "simple": "Vốn hóa thị trường = giá hiện tại × tổng số coin đang lưu hành. Đại diện tổng giá trị của một đồng coin. Bitcoin có vốn hóa ~1 nghìn tỷ USD, chiếm ~50% toàn bộ crypto.",
        "analogy": "Công ty có cổ phiếu 100k/cổ và 1 triệu cổ phiếu thì vốn hóa = 100 tỷ. Bitcoin ở 1.5 tỷ/BTC với 19.5 triệu BTC = vốn hóa ~29 nghìn tỷ đồng.",
        "key_points": [
            "Công thức: Giá × Lượng lưu hành",
            "Bitcoin dominance = vốn hóa BTC / tổng vốn hóa crypto",
            "Vốn hóa lớn = ổn định hơn, ít biến động hơn",
            "Coin vốn hóa nhỏ rủi ro cao nhưng tiềm năng tăng lớn hơn"
        ],
        "for_beginners": "Vốn hóa thị trường cho biết tổng giá trị của một đồng coin. Bitcoin có vốn hóa lớn nhất trong crypto. Coin có vốn hóa lớn thường an toàn hơn coin vốn hóa rất nhỏ."
    },

    "whale": {
        "simple": "Cá voi crypto là cá nhân hoặc tổ chức nắm giữ lượng lớn tiền điện tử - đủ để tác động đến giá thị trường khi mua hoặc bán.",
        "analogy": "Tưởng tượng đại dương mà các nhà đầu tư nhỏ là cá nhỏ. Cá voi to đến mức khi bơi, chúng tạo sóng lớn cuốn tất cả cá nhỏ đi. Cá voi Bitcoin có thể làm giá thay đổi mạnh.",
        "key_points": [
            "Không có định nghĩa chính thức, thường giữ 1.000+ BTC",
            "Chuyển động của cá voi theo dõi được trên blockchain công khai",
            "Giao dịch lớn của cá voi gây biến động giá cho người khác",
            "Cá voi nổi tiếng: Satoshi (~1M BTC), Grayscale, MicroStrategy"
        ],
        "for_beginners": "Cá voi là nhà đầu tư giữ lượng coin rất lớn. Khi cá voi bán, giá có thể giảm mạnh. Trader theo dõi ví cá voi để đoán xu hướng. Có công cụ như WhaleAlert thông báo mỗi khi cá voi di chuyển coin."
    },

    "leverage": {
        "simple": "Giao dịch đòn bẩy cho phép bạn kiểm soát vị thế lớn hơn số tiền thực có. Với đòn bẩy 10x, 1 triệu đồng kiểm soát vị thế 10 triệu - khuếch đại cả lợi nhuận lẫn thua lỗ.",
        "analogy": "Dùng đòn bẩy 10x để nâng ô tô: sức nhỏ, kết quả lớn. Nhưng nếu trượt, ô tô đè lên bạn. Đòn bẩy khuếch đại lợi nhuận nhưng có thể xóa sạch tài khoản trong tích tắc.",
        "key_points": [
            "Tỷ lệ đòn bẩy phổ biến: 2x, 5x, 10x, 20x, 100x",
            "Thanh lý (Liquidation): vị thế bị đóng bắt buộc khi lỗ quá nhiều",
            "Rất rủi ro - hơn 80% trader đòn bẩy thua lỗ",
            "Có trên Binance Futures, BitMEX, Bybit"
        ],
        "for_beginners": "Đòn bẩy cho bạn giao dịch với nhiều tiền hơn số bạn có. Đòn bẩy 10x: giá giảm 10% là mất toàn bộ vốn. Người mới TUYỆT ĐỐI không dùng đòn bẩy - rất dễ mất trắng."
    },

    "whitepaper": {
        "simple": "Whitepaper (sách trắng) là tài liệu kỹ thuật giải thích cách hoạt động của một đồng coin - công nghệ, mục đích và cách giải quyết vấn đề. Whitepaper Bitcoin của Satoshi Nakamoto được công bố ngày 31/10/2008.",
        "analogy": "Như bản kế hoạch kinh doanh cho một đồng coin. Nó giải thích 'tại sao' (vấn đề gì cần giải quyết) và 'như thế nào' (giải pháp kỹ thuật). Đọc whitepaper giúp đánh giá dự án có thật không.",
        "key_points": [
            "Tiêu đề whitepaper Bitcoin: 'Bitcoin: A Peer-to-Peer Electronic Cash System'",
            "Công bố ngày 31/10/2008 bởi Satoshi Nakamoto",
            "Chỉ 9 trang - một trong những tài liệu có tầm ảnh hưởng nhất lịch sử công nghệ",
            "Hầu hết scam không có whitepaper hoặc sao chép của người khác"
        ],
        "for_beginners": "Whitepaper Bitcoin là tài liệu gốc giải thích Bitcoin với thế giới. Trước khi đầu tư bất kỳ đồng coin nào, hãy kiểm tra có whitepaper không. Không có whitepaper = nhiều khả năng là lừa đảo."
    },
}

def get_education_response(concept: str, language: str = "en") -> str:
    """Get educational explanation for a crypto concept.
    
    Supports multiple question variations through the 'variations' dictionary.
    Returns formatted response with 4 sections: simple, analogy, key_points, for_beginners
    """
    concept_lower = concept.lower().strip()
    
    # Try to find in variations mapping first
    if concept_lower in variations:
        concept_key = variations[concept_lower]
    else:
        concept_key = concept_lower
    
    # Select the appropriate dictionary based on language
    if language == "vi":
        crypto_dict = CRYPTO_BASICS_VI
    else:
        crypto_dict = CRYPTO_BASICS_EN
    
    # Get the explanation if concept exists
    if concept_key in crypto_dict:
        info = crypto_dict[concept_key]
        key_points_text = "\n".join([f"• {point}" for point in info['key_points']])
        
        if language == "vi":
            return f"""{info['simple']}

📌 Ví dụ dễ hiểu: {info['analogy']}

🎯 Những điểm quan trọng:
{key_points_text}

👶 Cho người mới bắt đầu: {info['for_beginners']}"""
        else:
            return f"""{info['simple']}

📌 Easy analogy: {info['analogy']}

🎯 Key points:
{key_points_text}

👶 For beginners: {info['for_beginners']}"""
    
    # No concept found - return helpful message
    if language == "vi":
        return f"Tôi chưa có thông tin về '{concept}' lúc này. Hãy thử hỏi về: Bitcoin, Ethereum, Blockchain, Tiền điện tử, Ví, Sàn giao dịch, Mining, Halving hoặc Thị trường."
    else:
        return f"I don't have information about '{concept}' yet. Try asking about: Bitcoin, Ethereum, Blockchain, Cryptocurrency, Wallet, Exchange, Mining, Halving, or Markets."
