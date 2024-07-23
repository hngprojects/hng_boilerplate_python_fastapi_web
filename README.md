# Contribute to the hng_boilerplate_python_fastapi_web Project by Forking and Using Your Terminal to Get Upstream Updates

Contributing to a GitHub project by forking and using your terminal to get upstream updates involves several steps. Here's a detailed explanation:

## 1. Fork the Repository
Forking a repository creates a personal copy of the project on your GitHub. This allows you to make changes without affecting the original project.

- Go to the GitHub repository you want to contribute to. [here click](https://github.com/hngprojects/hng_boilerplate_python_fastapi_web)
- Click on the "Fork" button at the top-right corner of the repository page.
This will create a copy of the repository under your GitHub account.

## 2. Clone the Forked Repository
Clone the forked repository to your local machine so you can work on it.

In this case
```sh
git clone https://github.com/your-username/hng_boilerplate_python_fastapi_web.git
cd hng_boilerplate_python_fastapi_web
```
- **REMEMBER to replace your-username with your GitHub username**

## 3. Configure the Upstream Repository
To keep your fork up-to-date with the original repository, you need to configure a remote that points to the original repository (upstream repository).

In this case
```sh
git remote add upstream https://github.com/hngprojects/hng_boilerplate_python_fastapi_web.git
```

## 4. Fetch and Merge Upstream Changes
To keep your fork in sync with the upstream repository, fetch the changes and merge them into your local repository.

```sh
git fetch upstream
git checkout dev
git merge upstream/dev
```
**Replace dev with the name of the branch you want to sync with.**

### Important: list all branches available in the upstream repository:

```sh
git branch -r
```

## 5. Create a New Branch
Create a new branch for your feature or bug fix. This keeps your changes organized and separate from the main branch.

```sh
git checkout -b feature/branch-name
```
- **Replace branch-name with a descriptive name for your branch.**

## 6. Make Changes and Commit
Make your changes to the code. Once you're satisfied with your changes, commit them to your new branch.

```sh
git add .
git commit -m "Description of the changes"
```

## 7. Push Changes to Your Fork
Push your changes to the corresponding branch in your forked repository on GitHub.

```sh
git push origin feature/branch-name
```

## 8. Create a Pull Request
To contribute your changes back to the original repository, you need to create a pull request.

- Go to your forked repository on GitHub.
- Switch to the branch you pushed your changes to.
- Click the "Pull Request" button.
- Add a descriptive title and detailed description for your pull request.
- Submit the pull request.
  
## 9. Keep Your Fork Updated
Regularly fetch and merge upstream changes to keep your fork up-to-date.

```sh
git fetch upstream
git checkout main
git merge upstream/dev
git push origin dev
```
- This ensures that your fork stays current with the original repository, minimizing merge conflicts and making it easier to contribute in the future.

## Summary
- Fork the repository on GitHub.
- Clone your fork to your local machine.
- Add the upstream repository as a remote.
- Fetch and merge upstream changes to keep your fork updated.
- Create a new branch for your changes.
- Make changes and commit them to your branch.
- Push your changes to your fork on GitHub.
- Create a pull request to contribute your changes back to the original repository.
- Regularly update your fork with upstream changes.

  
By following these steps, you can effectively contribute to the hng_boilerplate_python_fastapi_web projects while keeping your fork and local repository up-to-date with the original project.
