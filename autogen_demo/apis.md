# 博查AI搜索API接口
  
```yaml
openapi: 3.0.3
info:
  title: 博查AI搜索
  description: 从博查搜索网页信息和网页链接，搜索结果准确、完整，更适合AI使用。
  version: 1.0.0
servers:
  - url: https://api.bochaai.com/v1
paths:
  /web-search:
    post:
      summary: 从近百亿网页和生态内容源中搜索高质量世界知识，例如新闻、图片、百科、文库等。
      operationId: WebSearch
      requestBody:
        description: 请求参数
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                  description: 搜索关键字或语句
                  example: "阿里巴巴2024年的ESG报告"
                summary:
                  type: boolean
                  description: 是否在搜索结果中包含摘要
                  example: true
                freshness:
                  type: string
                  description: 搜索指定时间范围内的网页（可选值 "noLimit"、"oneDay"、"oneWeek"、"oneMonth"、"oneYear"）
                  default: "noLimit"
                  enum:
                    - "noLimit"
                    - "oneDay"
                    - "oneWeek"
                    - "oneMonth"
                    - "oneYear"
                  example: "noLimit"
                count:
                  type: integer
                  description: 返回的搜索结果数量（1-8），默认为8
                  default: 10
                  minimum: 1
                  maximum: 50
                  example: 20
              required:
                - query
                - count
      responses:
        '200':
          description: 成功的搜索响应
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                    description: 响应的状态码
                    example: 200
                  log_id:
                    type: string
                    description: 请求的唯一日志ID
                    example: "0d0eb34abc6eec9d"
                  msg:
                    type: string
                    nullable: true
                    description: 请求的消息提示（如果有的话）
                    example: null
                  data:
                    type: object
                    properties:
                      _type:
                        type: string
                        description: 搜索的类型
                        example: "SearchResponse"
                      queryContext:
                        type: object
                        properties:
                          originalQuery:
                            type: string
                            description: 原始的搜索关键字
                            example: "阿里巴巴2024年的ESG报告"
                      webPages:
                        type: object
                        properties:
                          webSearchUrl:
                            type: string
                            description: 网页搜索的URL
                            example: "https://bochaai.com/search?q=阿里巴巴2024年的ESG报告"
                          totalEstimatedMatches:
                            type: integer
                            description: 搜索匹配的网页总数
                            example: 1618000
                          value:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                  nullable: true
                                  description: 网页的排序ID
                                name:
                                  type: string
                                  description: 网页的标题
                                url:
                                  type: string
                                  description: 网页的URL
                                displayUrl:
                                  type: string
                                  description: 网页的展示URL
                                snippet:
                                  type: string
                                  description: 网页内容的简短描述
                                summary:
                                  type: string
                                  description: 网页内容的文本摘要
                                siteName:
                                  type: string
                                  description: 网页的网站名称
                                siteIcon:
                                  type: string
                                  description: 网页的网站图标
                                datePublished:
                                  type: string
                                  format: date-time
                                  description: 网页的发布时间
                                dateLastCrawled:
                                  type: string
                                  format: date-time
                                  description: 网页的收录时间或发布时间
                                cachedPageUrl:
                                  type: string
                                  nullable: true
                                  description: 网页的缓存页面URL
                                language:
                                  type: string
                                  nullable: true
                                  description: 网页的语言
                                isFamilyFriendly:
                                  type: boolean
                                  nullable: true
                                  description: 是否为家庭友好的页面
                                isNavigational:
                                  type: boolean
                                  nullable: true
                                  description: 是否为导航性页面
                      images:
                        type: object
                        properties:
                          id:
                            type: string
                            nullable: true
                            description: 图片搜索结果的ID
                          webSearchUrl:
                            type: string
                            nullable: true
                            description: 图片搜索的URL
                          value:
                            type: array
                            items:
                              type: object
                              properties:
                                webSearchUrl:
                                  type: string
                                  nullable: true
                                  description: 图片搜索结果的URL
                                name:
                                  type: string
                                  nullable: true
                                  description: 图片的名称
                                thumbnailUrl:
                                  type: string
                                  description: 图像缩略图的URL
                                  example: "http://dayu-img.uc.cn/columbus/img/oc/1002/45628755e2db09ccf7e6ea3bf22ad2b0.jpg"
                                datePublished:
                                  type: string
                                  nullable: true
                                  description: 图像的发布日期
                                contentUrl:
                                  type: string
                                  description: 访问全尺寸图像的URL
                                  example: "http://dayu-img.uc.cn/columbus/img/oc/1002/45628755e2db09ccf7e6ea3bf22ad2b0.jpg"
                                hostPageUrl:
                                  type: string
                                  description: 图片所在网页的URL
                                  example: "http://dayu-img.uc.cn/columbus/img/oc/1002/45628755e2db09ccf7e6ea3bf22ad2b0.jpg"
                                contentSize:
                                  type: string
                                  nullable: true
                                  description: 图片内容的大小
                                encodingFormat:
                                  type: string
                                  nullable: true
                                  description: 图片的编码格式
                                hostPageDisplayUrl:
                                  type: string
                                  nullable: true
                                  description: 图片所在网页的显示URL
                                width:
                                  type: integer
                                  description: 图片的宽度
                                  example: 553
                                height:
                                  type: integer
                                  description: 图片的高度
                                  example: 311
                                thumbnail:
                                  type: string
                                  nullable: true
                                  description: 图片缩略图（如果有的话）
                      videos:
                        type: object
                        properties:
                          id:
                            type: string
                            nullable: true
                            description: 视频搜索结果的ID
                          readLink:
                            type: string
                            nullable: true
                            description: 视频的读取链接
                          webSearchUrl:
                            type: string
                            nullable: true
                            description: 视频搜索的URL
                          isFamilyFriendly:
                            type: boolean
                            description: 是否为家庭友好的视频
                          scenario:
                            type: string
                            description: 视频的场景
                          value:
                            type: array
                            items:
                              type: object
                              properties:
                                webSearchUrl:
                                  type: string
                                  description: 视频搜索结果的URL
                                name:
                                  type: string
                                  description: 视频的名称
                                description:
                                  type: string
                                  description: 视频的描述
                                thumbnailUrl:
                                  type: string
                                  description: 视频的缩略图URL
                                publisher:
                                  type: array
                                  items:
                                    type: object
                                    properties:
                                      name:
                                        type: string
                                        description: 发布者名称
                                creator:
                                  type: object
                                  properties:
                                    name:
                                      type: string
                                      description: 创作者名称
                                contentUrl:
                                  type: string
                                  description: 视频内容的URL
                                hostPageUrl:
                                  type: string
                                  description: 视频所在网页的URL
                                encodingFormat:
                                  type: string
                                  description: 视频编码格式
                                hostPageDisplayUrl:
                                  type: string
                                  description: 视频所在网页的显示URL
                                width:
                                  type: integer
                                  description: 视频的宽度
                                height:
                                  type: integer
                                  description: 视频的高度
                                duration:
                                  type: string
                                  description: 视频的长度
                                motionThumbnailUrl:
                                  type: string
                                  description: 动态缩略图的URL
                                embedHtml:
                                  type: string
                                  description: 用于嵌入视频的HTML代码
                                allowHttpsEmbed:
                                  type: boolean
                                  description: 是否允许HTTPS嵌入
                                viewCount:
                                  type: integer
                                  description: 视频的观看次数
                                thumbnail:
                                  type: object
                                  properties:
                                    height:
                                      type: integer
                                      description: 视频缩略图的高度
                                    width:
                                      type: integer
                                      description: 视频缩略图的宽度
                                allowMobileEmbed:
                                  type: boolean
                                  description: 是否允许移动端嵌入
                                isSuperfresh:
                                  type: boolean
                                  description: 是否为最新视频
                                datePublished:
                                  type: string
                                  description: 视频的发布日期
        '400':
          description: 请求参数错误
        '401':
          description: 未授权 - API 密钥无效或缺失
        '500':
          description: 搜索服务内部错误
      security:
        - apiKeyAuth: []
components:
  securitySchemes:
    apiKeyAuth:
      type: apiKey
      in: header
      name: Bearen token
      description: API密钥验证，值为 sk-9cbba1e7a74d4dbd885302ec587efd13
```

---

# SearXNG搜索API接口

```yaml
openapi: 3.0.1
info:
  title: SearXNG搜索API接口
  description: ''
  version: 1.0.0
tags: []
servers:
  - url: http://39.155.179.4:8088
paths:
  /search?format=json&language=zh-CN&safesearch=0:
    get:
      summary: 查询搜索引擎
      deprecated: false
      description: ''
      tags: []
      parameters:
        - name: format
          in: query
          description: 输出格式
          required: false
          example: json
          schema:
            type: string
        - name: q
          in: query
          description: 搜索问题
          required: false
          example: 新能源
          schema:
            type: string
        - name: language
          in: query
          description: 搜索语言
          required: false
          example: zh-CN
          schema:
            type: string
        - name: time_range
          in: query
          description: ''
          required: false
          example: ''
          schema:
            type: string
        - name: safesearch
          in: query
          description: 安全搜索
          required: false
          example: '0'
          schema:
            type: string
        - name: categories
          in: query
          description: general 搜索新闻和图片  ，images 搜索图片
          required: false
          example: general
          schema:
            type: string
        - name: pageno
          in: query
          description: 页号 例如1 ，2
          required: false
          example: 1
          schema:
            type: integer
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties:
                  query:
                    type: string
                    description: 查询的关键词
                  number_of_results:
                    type: integer
                    description: 无实际意义
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        title:
                          type: string
                          description: 搜索结果的标题
                        url:
                          type: string
                          description: 搜索结果的 URL 地址
                        content:
                          type: string
                          description: 搜索结果的内容摘要
                        engine:
                          type: string
                          description: 搜索结果的搜索引擎
                        template:
                          type: string
                          description: 用于渲染该结果的模板
                        parsed_url:
                          type: array
                          items:
                            type: string
                          description: ' 解析的 URL 组成部分，通常为 [协议, 主机名, 路径, 查询参数, 等等]。这一部分帮助处理 URL 的拆解'
                          nullable: true
                        img_src:
                          type: string
                          description: 结果中的图片来源（如果有的话），为空则表示没有图片
                        thumbnail:
                          type: string
                          description: 结果的缩略图（如果有的话），为空则表示没有缩略图
                        priority:
                          type: string
                          description: 果的优先级，可能是一个数字或标识符，表明结果的排序优先级
                        engines:
                          type: array
                          items:
                            type: string
                          description: 返回该搜索结果的搜索引擎列表
                        positions:
                          type: array
                          items:
                            type: integer
                          description: 结果在搜索引擎中的排名位置
                        score:
                          type: integer
                          description: 该搜索结果的相关性分数，数值越高表示与查询越相关
                        category:
                          type: string
                          description: 搜索结果所属的类别。通常有多个预设类别，如 general（一般）、news（新闻）
                        publishedDate:
                          type: string
                          description: 发布时间
                      required:
                        - title
                        - url
                        - content
                        - engine
                        - img_src
                        - thumbnail
                        - priority
                        - engines
                        - positions
                        - score
                        - category
                        - publishedDate
                  answers:
                    type: array
                    items:
                      type: string
                    description: 索引擎提供了直接回答
                  corrections:
                    type: array
                    items:
                      type: string
                    description: 查询有拼写错误或需要更正，相关的纠正建议
                  infoboxes:
                    type: array
                    items:
                      type: string
                    description: 如果搜索结果提供了信息框或重要信息摘要
                  suggestions:
                    type: array
                    items:
                      type: string
                    description: 搜索引擎建议了其他的查询关键词或改进建议
                  unresponsive_engines:
                    type: array
                    items:
                      type: array
                      items:
                        type: string
                        description: 错误信息
                      description: 引擎名
                    description: 表示哪些搜索引擎未响应或出现了错误，包含引擎名和错误信息。
                required:
                  - query
                  - results
                  - answers
                  - corrections
                  - infoboxes
                  - suggestions
                  - unresponsive_engines
              example:
                query: 新能源
                number_of_results: 0
                results:
                  - title: OFweek新能源汽车网 - 新能源汽车行业门户
                    url: https://nev.ofweek.com/
                    content: >-
                      2025年5月25日 -
                      市场研究奥迪,电动汽车,欧洲,本田,新能源2025-06-25.OFweek新能源汽车网,提供及时准确的行业资讯,以独特的视角报道热点事件,包括新能源汽车前景、价格...
                    engine: 360search
                    template: default.html
                    parsed_url:
                      - https
                      - nev.ofweek.com
                      - /
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - 360search
                    positions:
                      - 1
                    score: 1
                    category: general
                  - title: 新能源科学与工程
                    url: https://dqxy.sdju.edu.cn/xnykxygc/main.psp
                    content: >-
                      学生受益面广,能力提升明显,产生了一批优秀成果,新能源科学与工程专业本科生参加的科创团队分别获得2016年
                      “创青春”中航工业全国大学生创业大赛银奖。2016年本专业本科生参加的第九届全国大学生节能减排大赛,荣获二等奖。第七届中国国际“互联网+”大学生创新创业大赛上海赛区铜奖;第十一届全国大学生电子商务“创新、创意
                    publishedDate: '2024-09-02T16:00:00'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - dqxy.sdju.edu.cn
                      - /xnykxygc/main.psp
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 1
                    score: 1
                    category: general
                  - title: 新能源汽车_纯电动汽车-CNEV新能源汽车网
                    url: http://www.chinanev.net/
                    content: >-
                      CNEV新能源汽车网是一家聚焦新能源汽车,纯电动汽车及相关产业领域,为新能源汽车行业内整车生产厂商、零部件供应商、经销商和广大用户提供实时网络资讯和整合资源...
                    engine: 360search
                    template: default.html
                    parsed_url:
                      - http
                      - www.chinanev.net
                      - /
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - 360search
                    positions:
                      - 2
                    score: 0.5
                    category: general
                  - title: 为啥越来越多买新能源的车主都后悔啦?新能源那可不是随便买的
                    url: >-
                      https://haokan.baidu.com/v?pd=wisenatural&vid=12412818750253854588
                    content: >-
                      我们医院一个同事新能源车开了18个月卖了,又换回油车。 2025-03-2210回复
                      昆唉尼6AI:电车是移动的火化炉,电车爆燃,瞬间高温焗死整车活人,无法自救逃生。现阶段买电车的人,都是一群等待活活烧死的大白鼠。以人为本珍爱生命,远离电车
                      2025-03-237回复 在佛子岭看美丽人生的红花刺槐:那是中奖500万的概率 2025...
                    publishedDate: '2025-03-21T15:07:48'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - haokan.baidu.com
                      - /v
                      - ''
                      - pd=wisenatural&vid=12412818750253854588
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 2
                    score: 0.5
                    category: general
                  - title: 集邦新能源网|Energytrend-太阳能光伏等新能源产业市场研究机构
                    url: https://www.energytrend.cn/
                    content: >-
                      根据TrendForce集邦咨询旗下新能源研究中心《全球光伏产业链价格趋势月报》最新调研数据,多晶硅和硅片价格下跌,价格难稳.集邦新能源获悉,2025年6月25日,赣锋锂业召开2024年...
                    engine: 360search
                    template: default.html
                    parsed_url:
                      - https
                      - www.energytrend.cn
                      - /
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - 360search
                    positions:
                      - 3
                    score: 0.3333333333333333
                    category: general
                  - title: 专业介绍|新能源科学与工程 - 哔哩哔哩
                    url: https://www.bilibili.com/read/cv27685334/
                    content: >-
                      新能源科学与工程属于工学门类,能源动力类专业大类,授予工学学位;高考招生专业为新能源科学与工程,2023年该专业的选考科目要求多为物理,而2024年该专业本科类的选考科目要求为物理&化学。
                      新能源是相对于常规能源而言,新能源是采用新技术和新材料而获得,在新技术基础上系统地开发利用的能源,如太阳能、风能、生物质能...
                    publishedDate: '2023-11-13T22:18:00'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - www.bilibili.com
                      - /read/cv27685334/
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 3
                    score: 0.3333333333333333
                    category: general
                  - title: 碳达峰、新能源科学与工程、储能科学与工程、能源动力之间的关系...
                    url: >-
                      https://baijiahao.baidu.com/s?id=1712150522673783179&wfr=spider&for=pc
                    content: >-
                      碳中和背景下，聊聊能源动力、新能源科学与工程、储能三个专业
                      这几天，网上讨论最多的是限电。限电好像各个省的原因不完全一样，但大家公认一点，跟碳达峰、碳中和的目标有关。作为一个紧密关注高考的博主，万事都能联系到高考。今天就来谈谈跟碳中和紧密相关的能源与动力工程、新能源科学与工程、储能科学与工程这...
                    publishedDate: '2021-09-28T12:59:39'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - baijiahao.baidu.com
                      - /s
                      - ''
                      - id=1712150522673783179&wfr=spider&for=pc
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 4
                    score: 0.25
                    category: general
                  - title: 新能源(US36977)_股票价格_行情_走势图—东方财富网
                    url: https://quote.eastmoney.com/q/202.US36977.html
                    content: >-
                      新能源US36977- 行情中心数据中心财经频道 - -- 今开:-最高:-成交量:-买入价:-内盘:-振幅:-
                      昨收:-最低:-成交额:-卖出价:-外盘:-量比:- 全球市场行情 更多 名称最新价涨跌幅 --- --- ---
                      --- --- --- --- --- --- ---
                    publishedDate: '2025-07-13T16:00:00'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - quote.eastmoney.com
                      - /q/202.US36977.html
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 5
                    score: 0.2
                    category: general
                  - title: 新能源科学与工程(本科 学制四年 工学学位) -攀枝花学院钒钛学院
                    url: https://ftxy.pzhu.cn/info/1528/8682.htm
                    content: >-
                      本专业培养适应区域经济社会发展需要,德智体美劳全面发展,艰苦奋斗、自律自强,具有较好自然、人文社会科学基础,掌握相应专业基本理论、基本技能和基本方法,具备相应专业能力、较强实践能力、自我获取知识能力、社会交往能力、组织管理能力、新能源材料的制造和性能评价等能力,能够从事新能源材料制备、工程管理、工程设计和运行...
                    publishedDate: '2025-04-10T09:53:23'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - ftxy.pzhu.cn
                      - /info/1528/8682.htm
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 6
                    score: 0.16666666666666666
                    category: general
                  - title: 【新能源汽车推荐】新能源汽车最新报价-新能源汽车有哪些-58汽车
                    url: https://m.58che.com/newpower/
                    content: >-
                      58汽车新能源频道,为您提供全国新能源汽车品牌、报价信息,看新能源汽车视频、资讯、图片、价格等信息,就上58汽车新能源频道。
                    publishedDate: '2025-07-03T16:00:00'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - m.58che.com
                      - /newpower/
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 7
                    score: 0.14285714285714285
                    category: general
                  - title: 新能源包括哪些
                    url: >-
                      https://localsite.baidu.com/site/wjzsorv8/8cd47d9a-7797-42f3-9306-b902ded71161?qaId=7837904&categoryLv1=%E6%95%99%E8%82%B2%E5%9F%B9%E8%AE%AD&efs=1&ch=54&srcid=10014&source=natural&category=%E5%85%B6%E4%BB%96&eduFrom=136&botSourceType=46
                    content: >-
                      新能源包括哪些?
                      新能源主要指替代传统化石能源(如煤炭、石油、天然气)的清洁、可再生或低碳能源类型,其核心特征包括环保性、可持续性和技术驱动性。根据国际能源署(IEA)的定义,新能源通常涵盖太阳能、风能、水能、核能、生物质能等主要类别,并在全球范围内逐步拓展至地热能、潮汐能、氢能...
                    publishedDate: '2025-05-22T06:21:15'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - localsite.baidu.com
                      - /site/wjzsorv8/8cd47d9a-7797-42f3-9306-b902ded71161
                      - ''
                      - >-
                        qaId=7837904&categoryLv1=%E6%95%99%E8%82%B2%E5%9F%B9%E8%AE%AD&efs=1&ch=54&srcid=10014&source=natural&category=%E5%85%B6%E4%BB%96&eduFrom=136&botSourceType=46
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 8
                    score: 0.125
                    category: general
                  - title: 新能源发电 - 百度百科
                    url: >-
                      https://baike.baidu.com/item/%E6%96%B0%E8%83%BD%E6%BA%90%E5%8F%91%E7%94%B5/3848075
                    content: >-
                      新能源是指在新技术基础上，系统开发利用的可再生能源，如太阳能、风能、生物质能、地热能、海洋能、氢能、核能等，新能源发电也就是利用现有的技术，通过上述的新型能源，实现发电的过程。但新能源发电具有间歇性、随机性、波动性等特点，要实现安全稳定用电，就必须配备足够多、足够灵活的调节性电源。2021年前11月...
                    publishedDate: '2025-07-03T01:50:03'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - baike.baidu.com
                      - >-
                        /item/%E6%96%B0%E8%83%BD%E6%BA%90%E5%8F%91%E7%94%B5/3848075
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 9
                    score: 0.1111111111111111
                    category: general
                  - title: 新能源产业(开发新能源的单位和企业的工作的过程) - 百度百科
                    url: >-
                      https://baike.baidu.com/item/%E6%96%B0%E8%83%BD%E6%BA%90%E4%BA%A7%E4%B8%9A/8691436
                    content: >-
                      新能源指刚开始开发利用或正在积极研究、有待推广的能源，如太阳能、地热能、风能、海洋能、生物质能和核聚变能等。2022年11月25日，吉林省人民政府办公厅印发《吉林省新能源产业高质量发展战略规划（2022—2030年）》。分类
                      1、新能源按其形成和来源分类：(1)、来自太阳辐射的能量，如：太阳能、水能、风能、生物...
                    publishedDate: '2025-06-14T17:11:57'
                    engine: baidu
                    template: default.html
                    parsed_url:
                      - https
                      - baike.baidu.com
                      - >-
                        /item/%E6%96%B0%E8%83%BD%E6%BA%90%E4%BA%A7%E4%B8%9A/8691436
                      - ''
                      - ''
                      - ''
                    img_src: ''
                    thumbnail: ''
                    priority: ''
                    engines:
                      - baidu
                    positions:
                      - 10
                    score: 0.1
                    category: general
                answers: []
                corrections: []
                infoboxes: []
                suggestions: []
                unresponsive_engines:
                  - - bing
                    - server API error
                  - - brave
                    - timeout
                  - - duckduckgo
                    - timeout
                  - - google
                    - timeout
                  - - startpage
                    - timeout
          headers: {}
      security: []
components:
  schemas: {}
  securitySchemes: {}
servers: []
security: []

``` 

# 多模态图片理解模型接口

```yaml
openapi: 3.0.1
info:
  title: 多模态聊天模型 API
  description: |
    这是一个多模态聊天模型的 API，支持同时处理文本和图像内容。
    用户可以通过上传图像的 URL 和相应的文本，获取模型的推理结果，模型可以对图像进行描述并结合文本生成更智能的回答。
  version: 1.0.0
servers:
  - url: 'http://39.155.179.4:9116/v1'
    description: 多模态模型服务
paths:
  /chat/completions:
    post:
      summary: 根据图像和文本输入生成模型回应
      operationId: generateMultiModalCompletion
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                model:
                  type: string
                  description: "模型名称，必须为 Qwen2.5-VL-7B-Instruct。"
                  example: "Qwen2.5-VL-7B-Instruct"
                stream:
                  type: boolean
                  description: 是否启用流式响应。
                messages:
                  type: array
                  description: 用户发送的消息数组，包含图像和文本信息。
                  items:
                    type: object
                    properties:
                      role:
                        type: string
                        enum: [user, system, assistant]
                        description: 消息发送者的角色。可选值：`user`（用户）、`system`（系统）、`assistant`（助手）。
                      content:
                        type: array
                        description: 消息内容，可以是图像或文本。
                        items:
                          oneOf:
                            - $ref: '#/components/schemas/TextContent'
                            - $ref: '#/components/schemas/ImageContent'
      responses:
        '200':
          description: 成功返回生成的回应。
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    description: 请求的唯一标识符。
                  object:
                    type: string
                    description: 对象类型，通常为 `chat.completion`。
                  created:
                    type: integer
                    description: 创建时间的 Unix 时间戳。
                  model:
                    type: string
                    description: 使用的模型名称。
                  choices:
                    type: array
                    items:
                      type: object
                      properties:
                        index:
                          type: integer
                          description: 生成回应的索引。
                        message:
                          type: object
                          properties:
                            role:
                              type: string
                              description: 消息发送者的角色（例如 `assistant`）。
                            content:
                              type: string
                              description: 模型生成的回答内容。
                            reasoning_content:
                              type: string
                              description: 推理过程的内容，通常为空。
                            tool_calls:
                              type: array
                              description: 如果有工具调用，会列出工具信息，通常为空。
                        finish_reason:
                          type: string
                          description: 生成结束的原因。
                  usage:
                    type: object
                    properties:
                      prompt_tokens:
                        type: integer
                        description: 请求中使用的 token 数量。
                      completion_tokens:
                        type: integer
                        description: 生成的回答中使用的 token 数量。
                      total_tokens:
                        type: integer
                        description: 总的 token 数量（请求 + 响应）。
        '400':
          description: 错误请求，可能是缺少必要字段或输入无效。
        '500':
          description: 服务器内部错误。

components:
  schemas:
    TextContent:
      type: object
      properties:
        type:
          type: string
          enum: [text]
          description: 内容类型，固定为 `text`。
        text:
          type: string
          description: 文本内容。
    ImageContent:
      type: object
      properties:
        type:
          type: string
          enum: [image_url]
          description: 内容类型，固定为 `image_url`。
        image_url:
          type: object
          properties:
            url:
              type: string
              format: uri
              description: 图像 URL 地址。
    Message:
      type: object
      properties:
        role:
          type: string
          enum: [user, system, assistant]
          description: 消息发送者的角色。
        content:
          type: array
          description: 消息内容，包含图像或文本内容。
          items:
            oneOf:
              - $ref: '#/components/schemas/TextContent'
              - $ref: '#/components/schemas/ImageContent'

    RequestBody:
      type: object
      properties:
        model:
          type: string
          description: "模型名称，必须为 Qwen2.5-VL-7B-Instruct。"
          example: "Qwen2.5-VL-7B-Instruct"
        stream:
          type: boolean
          description: 是否启用流式响应。
        messages:
          type: array
          description: 消息内容数组，每条消息可以包含图像或文本。
          items:
            $ref: '#/components/schemas/Message'

    ResponseBody:
      type: object
      properties:
        id:
          type: string
          description: 请求的唯一标识符。
        object:
          type: string
          description: 对象类型，通常是 `chat.completion`。
        created:
          type: integer
          description: 创建时间的 Unix 时间戳。
        model:
          type: string
          description: 使用的模型名称。
        choices:
          type: array
          items:
            type: object
            properties:
              index:
                type: integer
                description: 生成回应的索引。
              message:
                type: object
                properties:
                  role:
                    type: string
                    description: 消息发送者的角色（例如 `assistant`）。
                  content:
                    type: string
                    description: 模型生成的回答内容。
                  reasoning_content:
                    type: string
                    description: 推理过程的内容，通常为空。
                  tool_calls:
                    type: array
                    description: 如果有工具调用，会列出工具信息，通常为空。
              finish_reason:
                type: string
                description: 生成结束的原因。
        usage:
          type: object
          properties:
            prompt_tokens:
              type: integer
              description: 请求中使用的 token 数量。
            completion_tokens:
              type: integer
              description: 生成的回答中使用的 token 数量。
            total_tokens:
              type: integer
              description: 总的 token 数量（请求 + 响应）。

  examples:
    RequestExample:
      value:
        model: "Qwen2.5-VL-7B-Instruct"
        stream: false
        messages:
          - role: "user"
            content:
              - type: "image_url"
                image_url:
                  url: "https://img95.699pic.com/photo/40241/6812.jpg_wh300.jpg!/fh/300/quality/90"
              - type: "text"
                text: "你是一名专业的图片分析师，擅长解析图片中的内容与文字。 要求： 1.有非文字，则简述图片的内容 2. 图片中没有图像只有文字，则返回no_image"
    ResponseExample:
      value:
        id: "chatcmpl-abf30d2f99644f6eab5b0aac8e2f4313"
        object: "chat.completion"
        created: 1752645345
        model: "Qwen2.5-VL-7B-Instruct"
        choices:
          - index: 0
            message:
              role: "assistant"
              content: "这张图片展示了一个小型的能源系统模型。图中有太阳能板、风力发电机、建筑物和一个中央控制单元。太阳能板和风力发电机位于左侧，建筑物位于右侧，中央控制单元连接着这些设备，表示它们之间的能量传输关系。整体设计简洁明了，强调了可再生能源的应用。"
              reasoning_content: null
              tool_calls: []
            finish_reason: "stop"
        usage:
          prompt_tokens: 241
          completion_tokens: 67
          total_tokens: 308

```

# 模型访问接口
```yaml
openapi: 3.0.1
info:
  title: 聊天生成模型 API
  description: |
    这是一个聊天生成模型的 API，支持根据用户输入生成聊天回应。用户可以传递文本消息给模型，模型会根据设定的参数生成回应。支持的参数包括模型名称、温度、最大 token 数等。
  version: 1.0.0
servers:
  - url: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
    description: `qwen-plus` 模型服务
    security:
      - BearerAuth: []
  - url: 'http://61.49.53.5:30002/v1/chat/completions'
    description: `deepseek-v3-0528` 模型服务
  - url: 'http://61.49.53.5:30001/v1/chat/completions'
    description: `deepseek-r1` 模型服务

paths:
  /chat/completions:
    post:
      summary: 生成聊天回应
      operationId: generateChatCompletion
      tags:
        - 完成
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                model:
                  type: string
                  description: "模型名称，用于指定要使用的聊天生成模型。"
                  enum:
                    - "qwen-plus"
                    - "deepseek-v3-0528"
                    - "deepseek-r1"
                  example: "deepseek-v3-0528"
                temperature:
                  type: number
                  description: "生成结果的随机性。值越低，生成的回答越确定。"
                  example: 0.1
                top_p:
                  type: number
                  description: "用于控制生成样本的概率分布。设置为 1.0 表示不做截断。"
                  example: 1.0
                max_tokens:
                  type: integer
                  description: "生成文本的最大 token 数。"
                  example: 2048
                echo:
                  type: string
                  description: "是否回显用户输入。"
                  example: "False"
                stream:
                  type: boolean
                  description: "是否启用流式响应。"
                  example: false
                messages:
                  type: array
                  description: "用户消息的数组，每条消息有角色和内容。"
                  items:
                    type: object
                    properties:
                      role:
                        type: string
                        enum: [user, system, assistant]
                        description: "消息发送者的角色。"
                      content:
                        type: string
                        description: "消息的内容。"
      responses:
        '200':
          description: 成功生成聊天回应。
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    description: "请求的唯一标识符。"
                  object:
                    type: string
                    description: "响应对象类型，通常为 `chat.completion`。"
                  created:
                    type: integer
                    description: "创建时间的 Unix 时间戳。"
                  model:
                    type: string
                    description: "所使用的模型名称。"
                  choices:
                    type: array
                    items:
                      type: object
                      properties:
                        index:
                          type: integer
                          description: "回应的索引，通常为 0。"
                        message:
                          type: object
                          properties:
                            role:
                              type: string
                              description: "消息的发送者角色（如 `assistant`）。"
                            content:
                              type: string
                              description: "模型生成的回答内容。"
                            reasoning_content:
                              type: string
                              description: "推理内容，通常为空。"
                            tool_calls:
                              type: array
                              description: "如有调用其他工具，列出工具信息。"
                        finish_reason:
                          type: string
                          description: "生成完成的原因，通常为 `stop`。"
                  usage:
                    type: object
                    properties:
                      prompt_tokens:
                        type: integer
                        description: "请求中所用的 token 数量。"
                      completion_tokens:
                        type: integer
                        description: "生成的响应中所用的 token 数量。"
                      total_tokens:
                        type: integer
                        description: "总 token 数量（请求 + 响应）。"
        '400':
          description: 错误请求，通常是参数缺失或格式不正确。
        '500':
          description: 服务器内部错误。

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    Message:
      type: object
      properties:
        role:
          type: string
          enum: [user, system, assistant]
          description: "消息发送者的角色。"
        content:
          type: string
          description: "消息内容。"

    RequestBody:
      type: object
      properties:
        model:
          type: string
          description: "模型名称，用于指定聊天生成模型。"
          enum:
            - "qwen-plus"
            - "deepseek-v3-0528"
            - "deepseek-r1"
          example: "deepseek-v3-0528"
        temperature:
          type: number
          description: "生成结果的随机性。"
          example: 0.1
        top_p:
          type: number
          description: "控制生成样本的概率分布。"
          example: 1.0
        max_tokens:
          type: integer
          description: "生成文本的最大 token 数。"
          example: 2048
        echo:
          type: string
          description: "是否回显用户输入。"
          example: "False"
        stream:
          type: boolean
          description: "是否启用流式响应。"
          example: false
        messages:
          type: array
          description: "用户消息的数组。"
          items:
            $ref: '#/components/schemas/Message'

    ResponseBody:
      type: object
      properties:
        id:
          type: string
          description: "请求的唯一标识符。"
        object:
          type: string
          description: "响应对象类型，通常为 `chat.completion`。"
        created:
          type: integer
          description: "创建时间的 Unix 时间戳。"
        model:
          type: string
          description: "所使用的模型名称。"
        choices:
          type: array
          items:
            type: object
            properties:
              index:
                type: integer
                description: "回应的索引，通常为 0。"
              message:
                type: object
                properties:
                  role:
                    type: string
                    description: "消息发送者的角色（如 `assistant`）。"
                  content:
                    type: string
                    description: "模型生成的回答内容。"
                  reasoning_content:
                    type: string
                    description: "推理内容，通常为空。"
                  tool_calls:
                    type: array
                    description: "如有调用其他工具，列出工具信息。"
              finish_reason:
                type: string
                description: "生成完成的原因。"
        usage:
          type: object
          properties:
            prompt_tokens:
              type: integer
              description: "请求中所用的 token 数量。"
            completion_tokens:
              type: integer
              description: "生成的响应中所用的 token 数量。"
            total_tokens:
              type: integer
              description: "总的 token 数量（请求 + 响应）。"

  examples:
    RequestExample:
      value:
        model: "deepseek-v3-0528"
        temperature: 0.1
        top_p: 1.0
        max_tokens: 2048
        echo: "False"
        stream: false
        messages:
          - role: "user"
            content: "你好"
    ResponseExample:
      value:
        id: "d6ac07ecadce4b3ea651010cf57139e5"
        object: "chat.completion"
        created: 1752647345
        model: "deepseek-v3-0528"
        choices:
          - index: 0
            message:
              role: "assistant"
              content: "你好！😊 有什么可以帮你的吗？"
              reasoning_content: null
              tool_calls: null
            finish_reason: "stop"
        usage:
          prompt_tokens: 5
          total_tokens: 17
          completion_tokens: 12

```