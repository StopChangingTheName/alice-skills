import git

def commiting():
  repo = git.Repo('alice-skills')
  if repo.is_dirty(untracked_files = True):
    repo.index.add(['users.db', 'example.log'])
    repo.index.commit('DB & log change')