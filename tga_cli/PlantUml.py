# @startuml
# title Titanium Technology Gap Analysis (TGA) - Component Architecture (Tall + Narrow, Strong Left-Aligned)
#
# ' Layout
# top to bottom direction
# skinparam ranksep 70
# skinparam nodesep 30
# skinparam dpi 220
# skinparam padding 2
# skinparam shadowing false
# skinparam componentStyle rectangle
# skinparam packageStyle rectangle
#
# skinparam defaultFontName Arial
# skinparam defaultFontSize 11
# skinparam backgroundColor #FFFFFF
#
# skinparam wrapWidth 180
# skinparam maxMessageSize 120
#
# skinparam package {
#   BorderColor #2B2B2B
#   FontColor  #1F1F1F
#   RoundCorner 10
# }
#
# skinparam component {
#   BorderColor #2B2B2B
#   FontColor  #1F1F1F
#   BackgroundColor #F7F7F7
#   RoundCorner 8
# }
#
# skinparam interface {
#   BorderColor #2B2B2B
#   FontColor  #1F1F1F
#   BackgroundColor #FFF4D6
#   RoundCorner 8
# }
#
# skinparam arrow {
#   Color #4A4A4A
#   Thickness 1
# }
#
# ' Hard left anchors: use multiple spines to bias further left
# skinparam artifactBackgroundColor transparent
# skinparam artifactBorderColor transparent
# artifact " " as LEFT_A
# artifact " " as LEFT_B
#
# package "tga_cli" as PKG_ROOT #FFFFFF {
#
#   package "cli" as PKG_CLI #E8F1FF {
#     [__main__.py] as main
#     [args.py] as args
#     [controller.py] as controller
#   }
#
#   package "logging" as PKG_LOG #F3E8FF {
#     [setup.py] as log_setup
#   }
#
#   package "config" as PKG_CFG #EAF7EA {
#     [ini_config.py] as ini_config
#   }
#
#   [app_factory.py] as app_factory #FFFFFF
#
#   package "domain" as PKG_DOM #FFE8E8 {
#     [models.py] as domain_models
#     [errors.py] as domain_errors
#   }
#
#   package "services" as PKG_SVC #E8FFF5 {
#     [analysis_service.py] as analysis_service
#     [baseline_policy.py] as baseline_policy
#     [prompt_builder.py] as prompt_builder
#     [url_normalizer.py] as url_normalizer
#   }
#
#   package "ports" as PKG_PORTS #FFF4D6 {
#     interface "LLM\nPort" as ILLM
#     interface "Fetcher\nPort" as IFetcher
#     interface "Readers\nPort" as IReaders
#     interface "Renderers\nPort" as IRenderers
#     interface "Emailer\nPort" as IEmailer
#   }
#
#   package "infrastructure" as PKG_INFRA #F7F7F7 {
#
#     package "adapters" as PKG_ADAPTERS #FFF0E5 {
#       component "OpenAI\nAdapter" as AOpenAI
#       component "Requests\nFetcher" as AFetch
#       component "PDF\nReader" as APDF
#       component "DOCX\nReader" as ADOCX
#       component "Image\nReader" as AIMG
#       component "SMTP\nEmailer" as ASMTP
#     }
#
#     package "renderers" as PKG_RENDER #EDEBFF {
#       component "Markdown\nNormalizer" as MNorm
#       component "HTML\nRenderer" as RHTML
#       component "DOCX\nRenderer" as RDOCX
#       component "PPTX\nRenderer" as RPPTX
#     }
#
#     package "repositories" as PKG_REPO #E9F7FF {
#       component "Report\nRepository" as Repo
#     }
#
#     package "utils" as PKG_UTIL #F1F1F1 {
#       [text.py] as text_utils
#     }
#   }
# }
#
# ' --- STRONG LEFT ALIGNMENT (hidden) ---
# ' Use two anchors and tie them to the widest blocks to pull the whole layout left.
# LEFT_A -[hidden]-> main
# LEFT_A -[hidden]-> PKG_CLI
# LEFT_A -[hidden]-> PKG_CFG
# LEFT_A -[hidden]-> PKG_PORTS
# LEFT_A -[hidden]-> PKG_INFRA
#
# LEFT_B -[hidden]-> controller
# LEFT_B -[hidden]-> analysis_service
# LEFT_B -[hidden]-> PKG_SVC
# LEFT_B -[hidden]-> Repo
# LEFT_B -[hidden]-> text_utils
#
# ' --- Force vertical ordering (hidden links) ---
# main -[hidden]-> log_setup
# log_setup -[hidden]-> ini_config
# ini_config -[hidden]-> app_factory
# app_factory -[hidden]-> controller
# controller -[hidden]-> analysis_service
# analysis_service -[hidden]-> PKG_PORTS
# PKG_PORTS -[hidden]-> PKG_INFRA
# PKG_INFRA -[hidden]-> Repo
# Repo -[hidden]-> text_utils
#
# ' --- Visible relationships ---
# main -down-> args : parse
# main -down-> log_setup : logging
# main -down-> app_factory : wire
# main -down-> controller : run
# controller -down-> analysis_service : execute
#
# analysis_service ..> domain_models : uses
# analysis_service ..> domain_errors : raises
#
# analysis_service -down-> url_normalizer
# analysis_service -down-> baseline_policy
# analysis_service -down-> prompt_builder
# analysis_service -down-> Repo : paths
#
# analysis_service ..> IFetcher
# analysis_service ..> IReaders
# analysis_service ..> ILLM
# analysis_service ..> IRenderers
# analysis_service ..> IEmailer
#
# AOpenAI -down-|> ILLM
# AFetch  -down-|> IFetcher
# APDF    -down-|> IReaders
# ADOCX   -down-|> IReaders
# AIMG    -down-|> IReaders
# ASMTP   -down-|> IEmailer
#
# RHTML   -down-|> IRenderers
# RDOCX   -down-|> IRenderers
# RPPTX   -down-|> IRenderers
#
# RHTML -down-> MNorm
# RDOCX -down-> MNorm
# RPPTX -down-> MNorm
#
# app_factory ..> ini_config : settings
# app_factory ..> AOpenAI
# app_factory ..> AFetch
# app_factory ..> APDF
# app_factory ..> ADOCX
# app_factory ..> AIMG
# app_factory ..> ASMTP
# app_factory ..> RHTML
# app_factory ..> RDOCX
# app_factory ..> RPPTX
# app_factory ..> Repo
#
# @enduml
#
#
#
#
#
#
# @startuml
# title Titanium Technology Gap Analysis (TGA) - Component Architecture (Tall + Narrow)
#
# top to bottom direction
# skinparam ranksep 70
# skinparam nodesep 30
# skinparam dpi 220
# skinparam padding 18
# skinparam shadowing false
# skinparam componentStyle rectangle
# skinparam packageStyle rectangle
#
# skinparam defaultFontName Arial
# skinparam defaultFontSize 11
# skinparam backgroundColor #FFFFFF
#
# skinparam wrapWidth 180
# skinparam maxMessageSize 120
#
# skinparam package {
#   BorderColor #2B2B2B
#   FontColor  #1F1F1F
#   RoundCorner 10
# }
#
# skinparam component {
#   BorderColor #2B2B2B
#   FontColor  #1F1F1F
#   BackgroundColor #F7F7F7
#   RoundCorner 8
# }
#
# skinparam interface {
#   BorderColor #2B2B2B
#   FontColor  #1F1F1F
#   BackgroundColor #FFF4D6
#   RoundCorner 8
# }
#
# skinparam arrow {
#   Color #4A4A4A
#   Thickness 1
# }
#
# package "tga_cli" as PKG_ROOT #FFFFFF {
#
#   package "cli" as PKG_CLI #E8F1FF {
#     [__main__.py] as main
#     [args.py] as args
#     [controller.py] as controller
#   }
#
#   package "logging" as PKG_LOG #F3E8FF {
#     [setup.py] as log_setup
#   }
#
#   package "config" as PKG_CFG #EAF7EA {
#     [ini_config.py] as ini_config
#   }
#
#   [app_factory.py] as app_factory #FFFFFF
#
#   package "domain" as PKG_DOM #FFE8E8 {
#     [models.py] as domain_models
#     [errors.py] as domain_errors
#   }
#
#   package "services" as PKG_SVC #E8FFF5 {
#     [analysis_service.py] as analysis_service
#     [baseline_policy.py] as baseline_policy
#     [prompt_builder.py] as prompt_builder
#     [url_normalizer.py] as url_normalizer
#   }
#
#   package "ports" as PKG_PORTS #FFF4D6 {
#     interface "LLM\nPort" as ILLM
#     interface "Fetcher\nPort" as IFetcher
#     interface "Readers\nPort" as IReaders
#     interface "Renderers\nPort" as IRenderers
#     interface "Emailer\nPort" as IEmailer
#   }
#
#   ' Infrastructure cluster (keeps right-side modules from drifting outward)
#   package "infrastructure" as PKG_INFRA #F7F7F7 {
#
#     package "adapters" as PKG_ADAPTERS #FFF0E5 {
#       component "OpenAI\nAdapter" as AOpenAI
#       component "Requests\nFetcher" as AFetch
#       component "PDF\nReader" as APDF
#       component "DOCX\nReader" as ADOCX
#       component "Image\nReader" as AIMG
#       component "SMTP\nEmailer" as ASMTP
#     }
#
#     package "renderers" as PKG_RENDER #EDEBFF {
#       component "Markdown\nNormalizer" as MNorm
#       component "HTML\nRenderer" as RHTML
#       component "DOCX\nRenderer" as RDOCX
#       component "PPTX\nRenderer" as RPPTX
#     }
#
#     package "repositories" as PKG_REPO #E9F7FF {
#       component "Report\nRepository" as Repo
#     }
#
#     package "utils" as PKG_UTIL #F1F1F1 {
#       [text.py] as text_utils
#     }
#   }
# }
#
# ' --- Layout anchors (SAFE SYNTAX): hidden links WITHOUT direction keywords ---
# main -[hidden]-> log_setup
# log_setup -[hidden]-> ini_config
# ini_config -[hidden]-> app_factory
# app_factory -[hidden]-> controller
# controller -[hidden]-> analysis_service
#
# analysis_service -[hidden]-> PKG_PORTS
# PKG_PORTS -[hidden]-> PKG_INFRA
# PKG_INFRA -[hidden]-> Repo
# Repo -[hidden]-> text_utils
#
# ' Extra pull-left anchors (cross ties)
# PKG_CLI -[hidden]-> PKG_PORTS
# PKG_LOG -[hidden]-> PKG_PORTS
# PKG_CFG -[hidden]-> PKG_PORTS
# PKG_DOM -[hidden]-> PKG_PORTS
# PKG_SVC -[hidden]-> PKG_PORTS
#
# ' --- Visible relationships (keep labels short to avoid width) ---
# main -down-> args : parse
# main -down-> log_setup : logging
# main -down-> app_factory : wire
# main -down-> controller : run
# controller -down-> analysis_service : execute
#
# analysis_service ..> domain_models : uses
# analysis_service ..> domain_errors : raises
#
# analysis_service -down-> url_normalizer
# analysis_service -down-> baseline_policy
# analysis_service -down-> prompt_builder
# analysis_service -down-> Repo : paths
#
# analysis_service ..> IFetcher
# analysis_service ..> IReaders
# analysis_service ..> ILLM
# analysis_service ..> IRenderers
# analysis_service ..> IEmailer
#
# AOpenAI -down-|> ILLM
# AFetch  -down-|> IFetcher
# APDF    -down-|> IReaders
# ADOCX   -down-|> IReaders
# AIMG    -down-|> IReaders
# ASMTP   -down-|> IEmailer
#
# RHTML   -down-|> IRenderers
# RDOCX   -down-|> IRenderers
# RPPTX   -down-|> IRenderers
#
# RHTML -down-> MNorm
# RDOCX -down-> MNorm
# RPPTX -down-> MNorm
#
# app_factory ..> ini_config : settings
# app_factory ..> AOpenAI
# app_factory ..> AFetch
# app_factory ..> APDF
# app_factory ..> ADOCX
# app_factory ..> AIMG
# app_factory ..> ASMTP
# app_factory ..> RHTML
# app_factory ..> RDOCX
# app_factory ..> RPPTX
# app_factory ..> Repo
#
# @enduml
#
#
#
#
# mermaid
#
#
# %%{init:{
#   "flowchart":{
#     "curve":"linear",
#     "nodeSpacing":30,
#     "rankSpacing":18
#   },
#   "themeVariables":{
#     "fontFamily":"Arial",
#     "fontSize":"12px"
#   }
# }}%%
# flowchart LR
#   L1["CLI / Delivery<br/><br/>- __main__.py<br/>- cli/args.py<br/>- cli/controller.py"]:::cli
#   L2["Composition Root<br/><br/>- app_factory.py<br/><br/>Configuration + Logging<br/>- config/ini_config.py<br/>- logging/setup.py"]:::boot
#   L3["Application / Services<br/><br/>Orchestration<br/>- services/analysis_service.py<br/><br/>Policies + Builders + Validation<br/>- services/baseline_policy.py<br/>- services/prompt_builder.py<br/>- services/url_normalizer.py"]:::svc
#   L4["Domain<br/><br/>Models<br/>- domain/models.py<br/><br/>Errors<br/>- domain/errors.py"]:::dom
#   L5["Ports (Interfaces)<br/><br/>- ports/llm.py<br/>- ports/fetcher.py<br/>- ports/readers.py<br/>- ports/renderers.py<br/>- ports/emailer.py"]:::ports
#   L6["Adapters + Infrastructure<br/><br/>LLM + Fetch + Read<br/>- adapters/llm_openai.py<br/>- adapters/fetch_requests.py<br/>- adapters/readers_pdf.py<br/>- adapters/readers_docx.py<br/>- adapters/readers_image.py<br/>- adapters/email_smtp.py<br/><br/>Render + Persist + Utils<br/>- renderers/markdown_normalizer.py<br/>- renderers/html_renderer.py<br/>- renderers/docx_renderer.py<br/>- renderers/pptx_renderer.py<br/>- repositories/report_repository.py<br/>- utils/text.py"]:::adp
#
#   L1 -->|bootstraps| L2
#   L2 -->|wires deps| L3
#   L3 -->|uses| L4
#   L3 -->|depends on| L5
#   L3 -->|calls via ports| L6
#   L6 -.->|implements| L5
#
#   classDef cli fill:#E8F1FF,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef boot fill:#EAF7EA,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef svc fill:#E8FFF5,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef dom fill:#FFE8E8,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef ports fill:#FFF4D6,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef adp fill:#FFF0E5,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#
#   class L1 cli
#   class L2 boot
#   class L3 svc
#   class L4 dom
#   class L5 ports
#   class L6 adp
#
#
#
#
# %%{init: {
#   "flowchart": {
#     "curve": "linear",
#     "nodeSpacing": 10,
#     "rankSpacing": 34
#   },
#   "themeVariables": {
#     "fontFamily": "Arial",
#     "fontSize": "12px"
#   }
# }}%%
# flowchart TB
#   %% Taller + narrower: short labels, forced line breaks, extra vertical spacing
#
#   L1["CLI<br/>__main__ · args · controller"]:::cli
#   L2["Bootstrap<br/>factory · config · logging"]:::boot
#   L3["Services<br/>analysis · policy · prompt · url"]:::svc
#   L4["Domain<br/>models · errors"]:::dom
#   L5["Ports<br/>llm · fetch · read · render · email"]:::ports
#   L6["Adapters/IO<br/>openai · requests · readers · smtp<br/>renderers · repo · utils"]:::adp
#
#   L1 -->|start| L2
#   L2 -->|wire| L3
#   L3 -->|use| L4
#   L3 -->|depend| L5
#   L6 -.->|implement| L5
#   L3 -->|call| L6
#
#   classDef cli fill:#E8F1FF,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef boot fill:#EAF7EA,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef svc fill:#E8FFF5,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef dom fill:#FFE8E8,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef ports fill:#FFF4D6,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef adp fill:#FFF0E5,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#
#   class L1 cli
#   class L2 boot
#   class L3 svc
#   class L4 dom
#   class L5 ports
#   class L6 adp
#
#
#
#
# %%{init:{
#   "flowchart":{
#     "curve":"linear",
#     "nodeSpacing":12,
#     "rankSpacing":36
#   },
#   "themeVariables":{
#     "fontFamily":"Arial",
#     "fontSize":"12px"
#   }
# }}%%
# flowchart TB
#   L1["CLI / Delivery<br/><br/>- __main__.py<br/>- cli/args.py<br/>- cli/controller.py"]:::cli
#   L2["Composition Root<br/><br/>- app_factory.py<br/><br/>Configuration + Logging<br/>- config/ini_config.py<br/>- logging/setup.py"]:::boot
#   L3["Application / Services<br/><br/>Orchestration<br/>- services/analysis_service.py<br/><br/>Policies + Builders + Validation<br/>- services/baseline_policy.py<br/>- services/prompt_builder.py<br/>- services/url_normalizer.py"]:::svc
#   L4["Domain<br/><br/>Models<br/>- domain/models.py<br/><br/>Errors<br/>- domain/errors.py"]:::dom
#   L5["Ports (Interfaces)<br/><br/>- ports/llm.py<br/>- ports/fetcher.py<br/>- ports/readers.py<br/>- ports/renderers.py<br/>- ports/emailer.py"]:::ports
#   L6["Adapters + Infrastructure<br/><br/>LLM + Fetch + Read<br/>- adapters/llm_openai.py<br/>- adapters/fetch_requests.py<br/>- adapters/readers_pdf.py<br/>- adapters/readers_docx.py<br/>- adapters/readers_image.py<br/>- adapters/email_smtp.py<br/><br/>Render + Persist + Utils<br/>- renderers/markdown_normalizer.py<br/>- renderers/html_renderer.py<br/>- renderers/docx_renderer.py<br/>- renderers/pptx_renderer.py<br/>- repositories/report_repository.py<br/>- utils/text.py"]:::adp
#
#   L1 -->|bootstraps| L2
#   L2 -->|wires deps| L3
#   L3 -->|uses| L4
#   L3 -->|depends on| L5
#   L6 -.->|implements| L5
#   L3 -->|calls via ports| L6
#
#   classDef cli fill:#E8F1FF,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef boot fill:#EAF7EA,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef svc fill:#E8FFF5,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef dom fill:#FFE8E8,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef ports fill:#FFF4D6,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#   classDef adp fill:#FFF0E5,stroke:#2B2B2B,color:#1F1F1F,stroke-width:1px;
#
#   class L1 cli
#   class L2 boot
#   class L3 svc
#   class L4 dom
#   class L5 ports
#   class L6 adp
