import requests
from dotenv import load_dotenv
import os


load_dotenv()

url = "http://localhost:8080/github-webhook/fff"
data = {
    "action": "opened",
    "issue": {
     "url": "https://api.github.com/repos/octocat/Hello-World/issues/1347",
     "number": 1347,
    },
   "repository" : {
        "id": 1296269,
        "full_name": "octocat/Hello-World",
        "owner": {
            "login": "octocat",
            "id": 1,
        },
    },
   "sender": {
     "login": "octocat",
     "id": 1,
    }
} 
data2 = {
  "ref": "refs/heads/main",
  "before": "976b1c59c2f910353ab08ebadc011fbef26aeb75",
  "after": "45f806463983143ecd710ecef0a125ce17b2f8fb",
  "repository": {
    "id": 874941838,
    "node_id": "R_kgDONCaNjg",
    "name": "Webhooks-TG-bot",
    "full_name": "MrKrik/Webhooks-TG-bot",
    "private": True,
    "owner": {
      "name": "MrKrik",
      "email": "108891933+MrKrik@users.noreply.github.com",
      "login": "MrKrik",
      "id": 108891933,
      "node_id": "U_kgDOBn2PHQ",
      "avatar_url": "https://avatars.githubusercontent.com/u/108891933?v=4",
      "gravatar_id": "",
      "url": "https://api.github.com/users/MrKrik",
      "html_url": "https://github.com/MrKrik",
      "followers_url": "https://api.github.com/users/MrKrik/followers",
      "following_url": "https://api.github.com/users/MrKrik/following{/other_user}",
      "gists_url": "https://api.github.com/users/MrKrik/gists{/gist_id}",
      "starred_url": "https://api.github.com/users/MrKrik/starred{/owner}{/repo}",
      "subscriptions_url": "https://api.github.com/users/MrKrik/subscriptions",
      "organizations_url": "https://api.github.com/users/MrKrik/orgs",
      "repos_url": "https://api.github.com/users/MrKrik/repos",
      "events_url": "https://api.github.com/users/MrKrik/events{/privacy}",
      "received_events_url": "https://api.github.com/users/MrKrik/received_events",
      "type": "User",
      "user_view_type": "public",
      "site_admin": False
    },
    "html_url": "https://github.com/MrKrik/Webhooks-TG-bot",
    "description": None,
    "fork": False,
    "url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot",
    "forks_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/forks",
    "keys_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/keys{/key_id}",
    "collaborators_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/collaborators{/collaborator}",
    "teams_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/teams",
    "hooks_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/hooks",
    "issue_events_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/issues/events{/number}",
    "events_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/events",
    "assignees_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/assignees{/user}",
    "branches_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/branches{/branch}",
    "tags_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/tags",
    "blobs_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/git/blobs{/sha}",
    "git_tags_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/git/tags{/sha}",
    "git_refs_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/git/refs{/sha}",
    "trees_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/git/trees{/sha}",
    "statuses_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/statuses/{sha}",
    "languages_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/languages",
    "stargazers_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/stargazers",
    "contributors_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/contributors",
    "subscribers_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/subscribers",
    "subscription_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/subscription",
    "commits_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/commits{/sha}",
    "git_commits_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/git/commits{/sha}",
    "comments_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/comments{/number}",
    "issue_comment_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/issues/comments{/number}",
    "contents_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/contents/{+path}",
    "compare_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/compare/{base}...{head}",
    "merges_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/merges",
    "archive_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/{archive_format}{/ref}",
    "downloads_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/downloads",
    "issues_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/issues{/number}",
    "pulls_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/pulls{/number}",
    "milestones_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/milestones{/number}",
    "notifications_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/notifications{?since,all,participating}",
    "labels_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/labels{/name}",
    "releases_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/releases{/id}",
    "deployments_url": "https://api.github.com/repos/MrKrik/Webhooks-TG-bot/deployments",
    "created_at": 1729277110,
    "updated_at": "2025-05-25T15:34:46Z",
    "pushed_at": 1748465127,
    "git_url": "git://github.com/MrKrik/Webhooks-TG-bot.git",
    "ssh_url": "git@github.com:MrKrik/Webhooks-TG-bot.git",
    "clone_url": "https://github.com/MrKrik/Webhooks-TG-bot.git",
    "svn_url": "https://github.com/MrKrik/Webhooks-TG-bot",
    "homepage": None,
    "size": 83,
    "stargazers_count": 1,
    "watchers_count": 1,
    "language": "Python",
    "has_issues": True,
    "has_projects": True,
    "has_downloads": True,
    "has_wiki": False,
    "has_pages": False,
    "has_discussions": False,
    "forks_count": 0,
    "mirror_url": None,
    "archived": False,
    "disabled": False,
    "open_issues_count": 0,
    "license": None,
    "allow_forking": True,
    "is_template": False,
    "web_commit_signoff_required": False,
    "topics": [

    ],
    "visibility": "private",
    "forks": 0,
    "open_issues": 0,
    "watchers": 1,
    "default_branch": "main",
    "stargazers": 1,
    "master_branch": "main"
  },
  "pusher": {
    "name": "MrKrik",
    "email": "108891933+MrKrik@users.noreply.github.com"
  },
  "sender": {
    "login": "MrKrik",
    "id": 108891933,
    "node_id": "U_kgDOBn2PHQ",
    "avatar_url": "https://avatars.githubusercontent.com/u/108891933?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/MrKrik",
    "html_url": "https://github.com/MrKrik",
    "followers_url": "https://api.github.com/users/MrKrik/followers",
    "following_url": "https://api.github.com/users/MrKrik/following{/other_user}",
    "gists_url": "https://api.github.com/users/MrKrik/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/MrKrik/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/MrKrik/subscriptions",
    "organizations_url": "https://api.github.com/users/MrKrik/orgs",
    "repos_url": "https://api.github.com/users/MrKrik/repos",
    "events_url": "https://api.github.com/users/MrKrik/events{/privacy}",
    "received_events_url": "https://api.github.com/users/MrKrik/received_events",
    "type": "User",
    "user_view_type": "public",
    "site_admin": False
  },
  "created": False,
  "deleted": False,
  "forced": False,
  "base_ref": None,
  "compare": "https://github.com/MrKrik/Webhooks-TG-bot/compare/976b1c59c2f9...45f806463983",
  "commits": [
    {
      "id": "45f806463983143ecd710ecef0a125ce17b2f8fb",
      "tree_id": "c661a8d907b243331a437bc155d178af4efc0485",
      "distinct": True,
      "message": "test",
      "timestamp": "2025-05-28T23:45:21+03:00",
      "url": "https://github.com/MrKrik/Webhooks-TG-bot/commit/45f806463983143ecd710ecef0a125ce17b2f8fb",
      "author": {
        "name": "MRK",
        "email": "MRQ"
      },
      "committer": {
        "name": "MRK",
        "email": "MRQ"
      },
      "added": [
        "__pycache__/db.cpython-313.pyc",
        "__pycache__/main.cpython-313.pyc",
        "go.mod",
        "go.sum",
        "handlers/__pycache__/create_webhook.cpython-313.pyc",
        "handlers/__pycache__/view_webhooks.cpython-313.pyc",
        "keyboards/__pycache__/menu.cpython-313.pyc"
      ],
      "removed": [

      ],
      "modified": [
        "main.go",
        "tests/__pycache__/config.cpython-313.pyc"
      ]
    }
  ],
  "head_commit": {
    "id": "45f806463983143ecd710ecef0a125ce17b2f8fb",
    "tree_id": "c661a8d907b243331a437bc155d178af4efc0485",
    "distinct": True,
    "message": "test",
    "timestamp": "2025-05-28T23:45:21+03:00",
    "url": "https://github.com/MrKrik/Webhooks-TG-bot/commit/45f806463983143ecd710ecef0a125ce17b2f8fb",
    "author": {
      "name": "MRK",
      "email": "MRQ"
    },
    "committer": {
      "name": "MRK",
      "email": "MRQ"
    },
    "added": [
      "__pycache__/db.cpython-313.pyc",
      "__pycache__/main.cpython-313.pyc",
      "go.mod",
      "go.sum",
      "handlers/__pycache__/create_webhook.cpython-313.pyc",
      "handlers/__pycache__/view_webhooks.cpython-313.pyc",
      "keyboards/__pycache__/menu.cpython-313.pyc"
    ],
    "removed": [

    ],
    "modified": [
      "main.go",
      "tests/__pycache__/config.cpython-313.pyc"
    ]
  }
}
headers = {'Content-Type': 'application/json', 'X-GitHub-Event': "push"}
response = requests.post(url, json=data2, headers=headers)
print(response.text)