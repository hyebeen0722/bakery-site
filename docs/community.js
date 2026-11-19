const api = (window.COMMUNITY_API || "").replace(/\/$/, "")
const filter = document.querySelector("#filter")
const container = document.querySelector("#posts")
const status = document.querySelector("#status")
const composer = document.querySelector("#compose")
const composeStatus = document.querySelector("#compose-status")
const template = document.querySelector("#comment-template")
let posts = []

const localMode = location.protocol === "file:"
document.querySelector("#local-note").hidden = !localMode

function localRequest(path, data) {
  const prefix = "bread-compass:board:v1:"
  const postId = path.split("/")[3]
  const bucket = postId ? prefix + "comments:" + postId + ":" : prefix + "posts:"
  let storage
  try {
    storage = window.localStorage
    if (data) {
      const record = Object.fromEntries(Object.entries(data).map(([key, value]) => [key, value.trim()]))
      if (Object.values(record).some(value => !value)) throw new TypeError("빈 항목을 채워 주세요.")
      const id = crypto.randomUUID()
      const created = new Date().toISOString().slice(0, -1)
      storage.setItem(bucket + id, JSON.stringify({ ...record, id, created }))
      return { id }
    }
    const keys = Object.keys(storage)
    const rows = keys.filter(key => key.startsWith(bucket)).map(key => JSON.parse(storage.getItem(key)))
    if (postId) return rows.sort((a, b) => a.created.localeCompare(b.created))
    for (const post of rows) {
      const commentPrefix = prefix + "comments:" + post.id + ":"
      post.comment_count = keys.filter(key => key.startsWith(commentPrefix)).length
    }
    return rows.sort((a, b) => b.created.localeCompare(a.created))
  } catch (error) {
    if (error instanceof TypeError && error.message === "빈 항목을 채워 주세요.") throw error
    throw new Error("이 브라우저의 파일 저장 공간을 사용할 수 없습니다. 일반 브라우저 창에서 다시 열어 주세요.")
  }
}

async function request(path, data) {
  if (localMode) return localRequest(path, data)
  const options = data ? {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  } : {}
  let response
  try {
    response = await fetch(api + path, options)
  } catch {
    throw new Error("서버에 연결할 수 없습니다.")
  }
  if (!response.headers.get("content-type")?.includes("application/json")) {
    throw new Error("커뮤니티 서버가 연결되어 있는지 확인해 주세요.")
  }
  const result = await response.json()
  if (!response.ok) throw new Error(result.error || "요청을 처리할 수 없습니다.")
  return result
}

function element(tag, text, className) {
  const node = document.createElement(tag)
  node.textContent = text
  if (className) node.className = className
  return node
}

function formatDate(value) {
  const date = new Date(value.replace(" ", "T") + "Z")
  return new Intl.DateTimeFormat("ko-KR", { dateStyle: "medium" }).format(date)
}

async function submit(event, message, path, onSaved) {
  event.preventDefault()
  const form = event.currentTarget
  const button = form.querySelector("button")
  button.disabled = true
  message.textContent = "등록 중입니다."
  try {
    await request(path, Object.fromEntries(new FormData(form)))
    form.reset()
    message.textContent = "등록했습니다."
    await onSaved()
  } catch (error) {
    message.textContent = error.message
  } finally {
    button.disabled = false
  }
}

function buildPost(post) {
  const article = element("article", "", "post")
  if (post.category === "매장 공지") article.dataset.notice = ""
  article.append(
    element("p", post.category + " · " + post.author + " · " + formatDate(post.created), "metadata"),
    element("h3", post.title),
    element("p", post.body, "post-body"),
  )

  const details = element("details", "")
  const summary = element("summary", "댓글 " + post.comment_count + "개")
  const list = element("div", "")
  const form = template.content.firstElementChild.cloneNode(true)
  const path = "/api/posts/" + post.id + "/comments"
  let refreshId = 0

  async function refreshComments() {
    const current = ++refreshId
    list.replaceChildren(element("p", "댓글을 불러오는 중입니다.", "metadata"))
    try {
      const comments = await request(path)
      if (current !== refreshId) return
      post.comment_count = comments.length
      summary.textContent = "댓글 " + comments.length + "개"
      const rows = comments.map(comment => {
        const row = element("div", "", "comment")
        row.append(element("strong", comment.author), element("p", comment.body))
        return row
      })
      list.replaceChildren(...rows)
      if (!rows.length) list.append(element("p", "첫 댓글을 남겨보세요.", "metadata"))
    } catch (error) {
      if (current === refreshId) list.replaceChildren(element("p", error.message))
    }
  }

  details.addEventListener("toggle", () => {
    if (details.open) refreshComments()
  })
  form.addEventListener("submit", event =>
    submit(event, form.querySelector("[role=status]"), path, refreshComments)
  )
  details.append(summary, list, form)
  article.append(details)
  return article
}

function render() {
  const visible = posts.filter(post => !filter.value || post.category === filter.value)
  status.textContent = visible.length ? "" : "등록된 게시글이 없습니다."
  container.replaceChildren(...visible.map(buildPost))
}

async function load() {
  try {
    posts = await request("/api/posts")
    render()
  } catch (error) {
    status.textContent = error.message
  }
}

if (localMode) window.addEventListener("storage", load)
filter.addEventListener("change", render)
composer.addEventListener("submit", event =>
  submit(event, composeStatus, "/api/posts", async () => {
    filter.value = ""
    await load()
  })
)
load()
