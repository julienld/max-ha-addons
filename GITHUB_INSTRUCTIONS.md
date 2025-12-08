# How to Publish "Max HA Addons" to GitHub

Since I cannot create the repository on your GitHub account for you, please follow these steps:

1.  **Create a new repository on GitHub**:
    *   Go to [https://github.com/new](https://github.com/new).
    *   Repository name: `max-ha-addons`
    *   Description: `Home Assistant Addons Repository`
    *   Public/Private: **Public** (Home Assistant needs to access it, unless you use authentication tokens, but Public is easiest for standard addons).
    *   Do **not** initialize with README, .gitignore, or License (we have local files).
    *   Click **Create repository**.

2.  **Push your local repository**:
    *   Copy the URL of your new repository (e.g., `https://github.com/maximeperron/max-ha-addons.git`).
    *   Run the following commands in your terminal (I have already done the 'git init' and 'git commit' parts for you):

    ```bash
    cd /Users/maximeperron/Documents/Antigravity/max-ha-addons
    git branch -M main
    git remote add origin https://github.com/maximeperron/max-ha-addons.git
    git push -u origin main
    ```

3.  **Add to Home Assistant**:
    *   In Home Assistant, go to **Settings** -> **Add-ons** -> **Add-on Store**.
    *   Click the **three dots** (top right) -> **Repositories**.
    *   Paste your GitHub repository URL: `https://github.com/maximeperron/max-ha-addons`.
    *   Click **Add**.
    *   The "Family Expenses Tracker" addon should now appear in the store.
