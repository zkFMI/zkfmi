# 日本語版の書き方（pages/ja/）

英語版 `pages/NAME.html` ごとに、同じファイル名で `pages/ja/NAME.html` を置く。
build.py が `ja/` 配下に出力し、ヘッダで言語を切り替える。翻訳は「英語の訳語を探す」
のではなく、**その文が何を言っているかを捉えて日本語で言い直す**。読み手は
金融市場基盤か暗号のどちらかに詳しい日本語話者。

## 変えてよいもの・変えてはいけないもの

変えてよい: テキストノード、`title:` と `description:`、見出しの文言、
`title=` / `aria-label=` / `alt=` / `placeholder=` 属性、mermaid 図のラベル、
`<summary>`、`<th>`、`<caption>`、`.next` の前後リンクの文言。

変えてはいけない:
- ヘッダの `path:` と `section:`（英語版と同一。build.py が `ja/` を付ける）
- HTML の構造（タグの並び、`id`、`class`、`href`、`colspan`、`data-*`）
- `<code>…</code>` と `<pre><code>…</code></pre>` の中身（識別子、コマンド、パス、JSON）
- `{{chart:NAME}}` トークン
- 数値・単位・日付・ハッシュ（`7.02 ms`、`3,424 B`、`2026-09-06`、`2.00×`）。
  英語版にある数字は日本語版にも必ず現れる（検査器が確認する）
- 固有名（zkPI, DeFMI, QOMM, OCLOB, DeKYX, DeCCP, Aethel, Canton, Renegade, MP-SPDZ,
  AvalancheGo, Bulletproofs, FROST, ristretto255, crate 名、論文著者名）
- 外部リンクの URL

mermaid: ラベルは日本語にしてよいが、構文は触らない。ラベル文中に `;` を入れない
（句点「。」か読点「、」を使う）。`<br/>` はそのまま。

検査: `python3 tools/check_ja.py pages/ja/NAME.html` が PASS になるまで直す。

## 書き方の規則

- 日本語と英数字の間は半角スペース 1 つ（`7 ノード`、`Pedersen commitment と範囲証明`、
  `3-of-7 の署名`）。数値と単位の間も英語版どおり（`7.02 ms`）。
- 句読点は「、」「。」。英語の `;` でつないだ文は二文に分ける。em ダッシュは使わず、
  読点か「。」にする。括弧は全角「（）」を日本語文中で、コード・数式には半角。
- 文体は「です・ます」ではなく **常体（〜する、〜である、〜ない）**。ただし
  既存の `90-ja-index.html` が丁寧体なので、`00-index.html`（表紙）だけは丁寧体でよい。
- 主張の強さを変えない。英語版が "not claimed" と言うところは「主張しない」、
  "measured" は「計測済み」、"smoke" は「smoke（動作確認レベル）」。強めない、弱めない。
- 造語の作法（全プロジェクト共通）: 英語術語の訳語を辞書から当てない。動作から
  組み立てる。定まらない語は名詞にせず動作で書く。
- 使わない語: 「取引所」（venue の訳に使わない）、「上流」（instruction source の
  訳に使わない）、「梯子」「バックオフ」「階層」（ladder の訳に使わない）。
- 英語のまま残す暗号用語（既存ページに合わせる）: commitment、note、ring、nullifier、
  handle、asset tag、quote proof、one-of-many、adaptor signature、finality、artifact、
  smoke、honest majority、malicious、abort、trusted dealer、host-a/b/c、gate（受入
  ゲート）。初出で必要なら括弧で短く補う。

## 用語表

| 英語 | 日本語 | 備考 |
|---|---|---|
| instruction source | 指図の発行元 | 文中では「指図を出す側」でもよい |
| venue | 市場 | QOMM と OCLOB。「取引所」は使わない |
| application | 業務システム | ファンド管理者、担保エンジン、銀行の審査、Aethel |
| settlement layer / ledger | 決済層 / 台帳 | |
| payment instruction | 決済指図 | zkPI = 証明付き決済指図 |
| commitment | commitment | |
| range proof | 範囲証明 | |
| product proof | 積の証明 | |
| sigma protocol | シグマ・プロトコル | |
| ring / anonymity set | ring / 匿名集合 | |
| decoy | おとり | |
| nullifier | nullifier | |
| note | note | |
| asset tag | asset tag | |
| viewing (scoped) | 閲覧（scope 付き） | |
| vetting | 審査証明（vetting） | crowd = 群 |
| reconciliation | 照合（正本台帳との） | |
| book-entry register | 振替口座簿 | |
| transfer institution / account management institution | 振替機関 / 口座管理機関 | |
| CSD | CSD（証券保管振替機関） | |
| CCP | 清算機関（CCP） | |
| FMI | 金融市場基盤（FMI） | |
| DvP / PvP | DvP / PvP | |
| netting | ネッティング | gross-gross / gross-net / net-net はそのまま |
| novation | 更改（novation） | |
| default waterfall | デフォルト・ウォーターフォール | |
| margin | 証拠金 | |
| collateral | 担保 | haircut = ヘアカット |
| intraday overdraft / limit | 日中当座貸越 / 限度 | |
| guarantee capacity | 保証枠 | |
| eligibility | 資格 | |
| presentation (DeKYX) | 提示 | |
| issuer | 発行者 | |
| revocation | 失効 | |
| reservation | 予約 | maker/taker reservation = メイカー予約 / テイカー予約 |
| admission (order) | 受付（順） | |
| matching | 照合 | |
| price-time priority | 価格・時間優先 | |
| best execution | 最良執行 | |
| RFQ | 見積依頼（RFQ） | |
| quote | 見積 | pricing policy = 値付け規則 |
| maker / taker | メイカー / テイカー | 初出で「値付けする側 / 依頼する側」を補ってよい |
| fill | 約定 | partial fill = 部分約定 |
| order book / CLOB | 板 / 連続指値板 | |
| depth per level | 価格帯別の合計 | |
| threshold | 閾値 | threshold signature = 閾値署名 |
| quorum | 定足数 | |
| committee | 委員会 | |
| validator (AvalancheGo, DeFMI) | 検証者 | |
| validator (Canton の役割) | validator | Canton の用語はそのまま |
| synchronizer (Canton) | synchronizer | |
| node | ノード | |
| host | ホスト | one host = 1 台のホスト |
| operator | 運営者 | computing entity = 計算主体 |
| independent operators | 独立した運営者 | |
| accountability | 説明責任 | |
| accountability ladder / rung n | 説明責任の段階 / 第 n 段 | 「梯子」は使わない |
| robustness / robust | 頑健性 / 頑健 | |
| security with abort | abort 付き安全性 | |
| public verifiability | 公開検証可能性 | |
| identifiable abort / blame | 責任者を特定できる abort / 責任の特定 | |
| matched field | 一致体（matched field） | MPC の体を commitment 群の位数に合わせる |
| binding | 束縛 | bind A to B = A を B に束縛する |
| soundness | 健全性 | |
| leakage | 漏れ | |
| differential privacy | 差分プライバシー | |
| offline / online phase | オフライン段階 / オンライン段階 | |
| preprocessing | 前処理 | |
| round | ラウンド | |
| wall clock | 壁時計時間 | traffic = 通信量 |
| throughput | 処理量 | latency = 遅延 |
| acceptance | 受入 | acceptance gate = 受入ゲート |
| built / accepted / measured | 実装済み / 受入済み / 計測済み | |
| research implementation | 研究実装 | |
| production | 本番 | |
| audit (external) | 監査 | audit machinery = 監査の仕組み |
| retracted claim | 撤回した主張 | |
| prior work | 先行研究 | |
| miss (prediction) | 外れ（予測の） | |
| open question | 未解決の問い | |
| trust boundary | 信頼境界 | |
| TEE | TEE | |
| hybrid signature / KEM | ハイブリッド署名 / KEM | |
| post-quantum | 耐量子 | |
| key exchange | 鍵交換 | |
| canonical preimage | 正規化した前像 | |
| wire (format) | wire 形式 | on the wire = wire 上 |
| vector (test) | テストベクタ | |
| receipt | 受領証 | |
| attestation | attestation | |
| selective disclosure | 選択的開示 | |
| pseudonymous | 仮名の | unlinkable = 連結不能 |
| finality | finality | legal finality = 法的 finality |
| Herstatt risk | ヘルシュタット・リスク | |
| fund subscription / redemption | ファンドの申込 / 解約 | |
| receivable | 債権 | payment stream = 支払ストリーム |
| servicing | サービシング | |

## ページ題名（nav と一致させる）

| ファイル | title |
|---|---|
| 00-index | zkFMI — 読めないものを決済する市場基盤 |
| 05-docs-index | ドキュメント一覧 |
| 06-principles | この研究の進め方 |
| 07-faq | よくある質問 |
| 10-architecture | 全体構成 |
| 20-zkpi | zkPI — 証明付き決済指図 |
| 21-defmi | DeFMI — 決済層 |
| 22-dekyx | DeKYX — 資格 |
| 23-deccp | DeCCP — 清算 |
| 30-qomm | QOMM — 依頼を見ない見積市場 |
| 31-oclob | OCLOB — 注文を見ない板 |
| 32-aethel | Aethel — 支払ストリームの債権化 |
| 33-use-cases | 市場以外の業務システム |
| 34-binding | 計算結果を commitment に束縛する |
| 35-audit | 監査の仕組み |
| 36-accountability | 説明責任と頑健性 |
| 37-deployment | 配置の選び方 |
| 40-measurements | 計測値 |
| 41-security | 安全性と信頼境界 |
| 42-prior-art | 先行研究との位置関係 |
| 43-regulation | 規制 |
| 44-status | 現状と受入 |
| 45-roadmap | 今後の計画 |
| 46-post-quantum | 耐量子化への移行 |
| 47-comparison | 他のシステムとの比較 |
| 50-get-started | 始め方 |
| 51-glossary | 用語集 |

## 読みやすさの基準（2026-09-07 追記、編集パスの指示）

一度訳した日本語版を、読者（金融市場基盤か暗号のどちらかに詳しい日本語話者）が
一読で意味を取れる文に直す。訳文であることを読者に感じさせない。

- 一文一義。英語の関係節や `;` でつないだ長文は、主語を立て直して二文以上に分ける。
  一文は 60 字前後まで。読点で三つ以上の節をつなげない。
- 主語と述語を近づける。「〜のは〜である」「〜ということ」の重ね掛けを避ける。
- 英語の修辞（倒置、皮肉、体言止めの畳語、"not X but Y" の直訳）は日本語の平叙文に
  言い直す。「〜、そして〜」の並列も文を分ける。
- 訳者が作った見慣れない漢語（例: 走行ハッシュ、零開封、一致体、基準線、盲化因子、
  台（support）、正本の受領証）は、動作や意味で言い直すか、初出で一言説明を添える。
  例: 「零開封」→「値が 0 であることを固定した開封証明」、「走行ハッシュ」→
  「追記のたびに更新するハッシュ」、「一致体（matched field）」→「MPC の体を
  commitment の群の位数に合わせた構成（matched field）」。
- 英語のまま残す術語（commitment、note、ring、nullifier、handle、artifact、smoke…）は
  初出で括弧か一言で意味を添える。「smoke」は「動作確認のみ（smoke）」。
- 数字と主張の強さは変えない。省略も追加もしない。構造・`<code>`・リンク・数値は
  検査器（tools/check_ja.py）が一致を確認する。
- 見出しは短い名詞句か動作の形。表のセルは体言止めでよい。
