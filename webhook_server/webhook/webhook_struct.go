package webhook

type github_issue struct {
	Url    string `json:"url"`
	Number int    `json:"number"`
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
	Url      string   `json:"url"`
	Message  string   `json:"message"`
	Added    []string `json:"added"`
	Removed  []string `json:"removed"`
	Modified []string `json:"modified"`
}

type Github_webhook struct {
	Id          string
	Action      string             `json:"action"`
	Issue       github_issue       `json:"issue"`
	Repository  github_repository  `json:"repository"`
	Sender      github_sender      `json:"sender"`
	Private     bool               `json:"private"`
	Full_name   string             `json:"full_name"`
	Head_commit github_head_commit `json:"head_commit"`
}
