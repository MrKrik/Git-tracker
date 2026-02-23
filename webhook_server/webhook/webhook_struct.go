package webhook

type github_issue struct {
	Id           int            `json:"id"`
	Url          string         `json:"url"`
	Html_url     string         `json:"html_url"`
	Number       int            `json:"number"`
	Title        string         `json:"title"`
	Body         string         `json:"body"`
	State        string         `json:"state"`
	State_reason string         `json:"state_reason"`
	User         github_sender  `json:"user"`
	Assignee     *github_sender `json:"assignee"`
	Labels       []github_label `json:"labels"`
	Created_at   string         `json:"created_at"`
	Updated_at   string         `json:"updated_at"`
	Closed_at    *string        `json:"closed_at"`
	Comments     int            `json:"comments"`
	Pull_request *interface{}   `json:"pull_request"`
}

type github_label struct {
	Id          int    `json:"id"`
	Url         string `json:"url"`
	Name        string `json:"name"`
	Color       string `json:"color"`
	Default     bool   `json:"default"`
	Description string `json:"description"`
}

type github_issue_comment struct {
	Id         int           `json:"id"`
	Url        string        `json:"url"`
	Html_url   string        `json:"html_url"`
	Body       string        `json:"body"`
	User       github_sender `json:"user"`
	Created_at string        `json:"created_at"`
	Updated_at string        `json:"updated_at"`
}

type github_issue_event struct {
	Action     string                `json:"action"`
	Issue      github_issue          `json:"issue"`
	Comment    *github_issue_comment `json:"comment"`
	Repository github_repository     `json:"repository"`
	Sender     github_sender         `json:"sender"`
}
type github_owner struct {
	Login   string `json:"login"`
	Id      int    `json:"id"`
	Node_id string `json:"node_id"`
}

type github_repository struct {
	Id        int          `json:"id"`
	Node_id   string       `json:"node_id"`
	Name      string       `json:"name"`
	Full_name string       `json:"full_name"`
	Private   bool         `json:"private"`
	Owner     github_owner `json:"owner"`
	Html_url  string       `json:"html_url"`
}

type github_sender struct {
	Url        string `json:"url"`
	Login      string `json:"login"`
	Id         int    `json:"id"`
	Avatar_url string `json:"avatar_url"`
}

type github_head_commit struct {
	Url       string               `json:"url"`
	Tree_url  string               `json:"tree_url"`
	Html_url  string               `json:"html_url"`
	Id        string               `json:"id"`
	Message   string               `json:"message"`
	Timestamp string               `json:"timestamp"`
	Author    github_commit_author `json:"author"`
	Committer github_commit_author `json:"committer"`
	Added     []string             `json:"added"`
	Removed   []string             `json:"removed"`
	Modified  []string             `json:"modified"`
}

type github_commit_author struct {
	Name     string `json:"name"`
	Email    string `json:"email"`
	Username string `json:"username"`
}

type github_pull_request struct {
	Id     int            `json:"id"`
	Number int            `json:"number"`
	Title  string         `json:"title"`
	Body   string         `json:"body"`
	Url    string         `json:"html_url"`
	State  string         `json:"state"`
	User   github_sender  `json:"user"`
	Base   github_pr_base `json:"base"`
	Head   github_pr_head `json:"head"`
}

type github_pr_base struct {
	Ref  string            `json:"ref"`
	Sha  string            `json:"sha"`
	Repo github_repository `json:"repo"`
}

type github_pr_head struct {
	Ref  string            `json:"ref"`
	Sha  string            `json:"sha"`
	Repo github_repository `json:"repo"`
}

type github_release struct {
	Id               int           `json:"id"`
	Tag_name         string        `json:"tag_name"`
	Target_commitish string        `json:"target_commitish"`
	Name             string        `json:"name"`
	Draft            bool          `json:"draft"`
	Prerelease       bool          `json:"prerelease"`
	Created_at       string        `json:"created_at"`
	Published_at     string        `json:"published_at"`
	Author           github_sender `json:"author"`
	Body             string        `json:"body"`
	Url              string        `json:"html_url"`
}

type github_push_event struct {
	Ref         string               `json:"ref"`
	Before      string               `json:"before"`
	After       string               `json:"after"`
	Created     bool                 `json:"created"`
	Deleted     bool                 `json:"deleted"`
	Forced      bool                 `json:"forced"`
	Repository  github_repository    `json:"repository"`
	Pusher      github_commit_author `json:"pusher"`
	Sender      github_sender        `json:"sender"`
	Commits     []github_head_commit `json:"commits"`
	Head_commit github_head_commit   `json:"head_commit"`
}

type Github_webhook struct {
	Id          string
	Action      string                `json:"action"`
	Issue       github_issue          `json:"issue"`
	Comment     *github_issue_comment `json:"comment"`
	Repository  github_repository     `json:"repository"`
	Sender      github_sender         `json:"sender"`
	Private     bool                  `json:"private"`
	Full_name   string                `json:"full_name"`
	Head_commit github_head_commit    `json:"head_commit"`
	PullRequest *github_pull_request  `json:"pull_request"`
	Release     *github_release       `json:"release"`
	Ref         string                `json:"ref"`
	Before      string                `json:"before"`
	After       string                `json:"after"`
	Created     bool                  `json:"created"`
	Deleted     bool                  `json:"deleted"`
	Forced      bool                  `json:"forced"`
	Commits     []github_head_commit  `json:"commits"`
}

// GetEventType возвращает тип события на основе полей
func (w *Github_webhook) GetEventType() string {
	if w.PullRequest != nil {
		return "pull_request"
	}
	if w.Release != nil {
		return "release"
	}
	if w.Issue.Number > 0 {
		return "issues"
	}
	if w.Ref != "" {
		return "push"
	}
	return "unknown"
}

// GetRepositoryName возвращает имя репозитория
func (w *Github_webhook) GetRepositoryName() string {
	if w.Repository.Name != "" {
		return w.Repository.Name
	}
	return w.Full_name
}

// GetRepositoryURL возвращает URL репозитория
func (w *Github_webhook) GetRepositoryURL() string {
	return w.Repository.Html_url
}

// GetAuthorLogin возвращает логин автора события
func (w *Github_webhook) GetAuthorLogin() string {
	if w.Sender.Login != "" {
		return w.Sender.Login
	}
	if w.PullRequest != nil && w.PullRequest.User.Login != "" {
		return w.PullRequest.User.Login
	}
	return "unknown"
}

// GetAuthorURL возвращает URL профиля автора
func (w *Github_webhook) GetAuthorURL() string {
	return w.Sender.Url
}

// GetAuthorAvatar возвращает URL аватара автора
func (w *Github_webhook) GetAuthorAvatar() string {
	return w.Sender.Avatar_url
}

// GetBranch возвращает имя ветки
func (w *Github_webhook) GetBranch() string {
	if w.Ref != "" {
		// Ref формат: "refs/heads/branch_name"
		parts := len(w.Ref)
		if parts > 11 {
			return w.Ref[11:] // Убираем "refs/heads/"
		}
		return w.Ref
	}
	if w.PullRequest != nil && w.PullRequest.Head.Ref != "" {
		return w.PullRequest.Head.Ref
	}
	return ""
}

// GetCommitMessage возвращает сообщение последнего коммита
func (w *Github_webhook) GetCommitMessage() string {
	if w.Head_commit.Message != "" {
		return w.Head_commit.Message
	}
	if len(w.Commits) > 0 {
		return w.Commits[len(w.Commits)-1].Message
	}
	return ""
}

// GetCommitCount возвращает количество коммитов
func (w *Github_webhook) GetCommitCount() int {
	return len(w.Commits)
}

// GetChangedFiles возвращает список изменённых файлов
func (w *Github_webhook) GetChangedFiles() []string {
	var files []string
	if w.Head_commit.Modified != nil {
		files = append(files, w.Head_commit.Modified...)
	}
	if w.Head_commit.Added != nil {
		files = append(files, w.Head_commit.Added...)
	}
	return files
}

// String возвращает строковое представление webhook события
func (w *Github_webhook) String() string {
	eventType := w.GetEventType()
	author := w.GetAuthorLogin()
	repo := w.GetRepositoryName()
	branch := w.GetBranch()

	switch eventType {
	case "push":
		return eventType + " to " + repo + ":" + branch + " by " + author
	case "pull_request":
		if w.PullRequest != nil {
			return "PR #" + string(rune(w.PullRequest.Number)) + " " + w.Action + " on " + repo
		}
	case "issues":
		return "Issue #" + string(rune(w.Issue.Number)) + " " + w.Action + " on " + repo
	case "release":
		if w.Release != nil {
			return "Release " + w.Release.Tag_name + " " + w.Action + " on " + repo
		}
	}

	return eventType + " on " + repo + " by " + author
}

// Issue Event Methods

// GetIssueNumber возвращает номер issue
func (w *Github_webhook) GetIssueNumber() int {
	return w.Issue.Number
}

// GetIssueTitle возвращает заголовок issue
func (w *Github_webhook) GetIssueTitle() string {
	return w.Issue.Title
}

// GetIssueBody возвращает описание issue
func (w *Github_webhook) GetIssueBody() string {
	return w.Issue.Body
}

// GetIssueState возвращает статус issue (open, closed)
func (w *Github_webhook) GetIssueState() string {
	return w.Issue.State
}

// GetIssueStateReason возвращает причину смены статуса (completed, not_planned, reopened)
func (w *Github_webhook) GetIssueStateReason() string {
	return w.Issue.State_reason
}

// GetIssueCreatedAt возвращает дату создания issue
func (w *Github_webhook) GetIssueCreatedAt() string {
	return w.Issue.Created_at
}

// GetIssueUpdatedAt возвращает дату последнего обновления issue
func (w *Github_webhook) GetIssueUpdatedAt() string {
	return w.Issue.Updated_at
}

// GetIssueClosedAt возвращает дату закрытия issue
func (w *Github_webhook) GetIssueClosedAt() string {
	if w.Issue.Closed_at != nil {
		return *w.Issue.Closed_at
	}
	return ""
}

// GetIssueAuthor возвращает автора issue
func (w *Github_webhook) GetIssueAuthor() string {
	return w.Issue.User.Login
}

// GetIssueAuthorURL возвращает URL профиля автора issue
func (w *Github_webhook) GetIssueAuthorURL() string {
	return w.Issue.User.Url
}

// GetIssueAssignee возвращает ответственного за issue
func (w *Github_webhook) GetIssueAssignee() string {
	if w.Issue.Assignee != nil {
		return w.Issue.Assignee.Login
	}
	return ""
}

// GetIssueLabels возвращает список меток на issue
func (w *Github_webhook) GetIssueLabels() []string {
	labels := make([]string, 0)
	for _, label := range w.Issue.Labels {
		labels = append(labels, label.Name)
	}
	return labels
}

// GetIssueCommentCount возвращает количество комментариев
func (w *Github_webhook) GetIssueCommentCount() int {
	return w.Issue.Comments
}

// GetCommentBody возвращает текст комментария (если это событие issue_comment)
func (w *Github_webhook) GetCommentBody() string {
	if w.Comment != nil {
		return w.Comment.Body
	}
	return ""
}

// GetCommentAuthor возвращает автора комментария
func (w *Github_webhook) GetCommentAuthor() string {
	if w.Comment != nil {
		return w.Comment.User.Login
	}
	return ""
}

// GetCommentAuthorURL возвращает URL профиля автора комментария
func (w *Github_webhook) GetCommentAuthorURL() string {
	if w.Comment != nil {
		return w.Comment.User.Url
	}
	return ""
}

// GetCommentCreatedAt возвращает дату создания комментария
func (w *Github_webhook) GetCommentCreatedAt() string {
	if w.Comment != nil {
		return w.Comment.Created_at
	}
	return ""
}

// IsIssueOpened проверяет, открыта ли issue
func (w *Github_webhook) IsIssueOpened() bool {
	return w.Issue.State == "open"
}

// IsIssueClosed проверяет, закрыта ли issue
func (w *Github_webhook) IsIssueClosed() bool {
	return w.Issue.State == "closed"
}

// GetIssueURL возвращает полный URL issue
func (w *Github_webhook) GetIssueURL() string {
	return w.Issue.Html_url
}

// FormatIssueMessage форматирует сообщение об issue для отправки
func (w *Github_webhook) FormatIssueMessage() string {
	action := w.Action
	issueNum := w.GetIssueNumber()
	issueTitle := w.GetIssueTitle()
	author := w.GetIssueAuthor()
	repo := w.GetRepositoryName()

	message := "[" + action + "] Issue #" + string(rune(issueNum)) + ": " + issueTitle
	message += "\nRepository: " + repo
	message += "\nAuthor: " + author

	if w.Comment != nil && w.Action == "created" {
		commentAuthor := w.GetCommentAuthor()
		commentBody := w.GetCommentBody()
		if len(commentBody) > 100 {
			commentBody = commentBody[:100] + "..."
		}
		message += "\nComment by " + commentAuthor + ": " + commentBody
	}

	message += "\nURL: " + w.GetIssueURL()

	return message
}

// GetIssueEventType возвращает тип события issue (opened, closed, reopened, edited, comment etc)
func (w *Github_webhook) GetIssueEventType() string {
	if w.Comment != nil {
		return "issue_comment_" + w.Action
	}
	return "issue_" + w.Action
}
