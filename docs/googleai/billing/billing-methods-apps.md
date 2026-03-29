# Billing

## Q1

It's completely understandable to feel a bit of "billing anxiety" once a bank card is linked to a developer account. Google's ecosystem can be a bit of a maze, especially when you're crossing the bridge from being a casual user to a developer.

Here is the breakdown of how your accounts, the app, and the billing actually work.

### 1. Is the Gemini App free?

**Yes, the "Basic" version of Gemini is free.**

For your "quick questions" on your phone or web browser, you are using the consumer version of Gemini.

  ***The Limits:** You get a generous amount of daily prompts, but if you hit the ceiling, it might temporarily downgrade you to a lighter model or ask you to wait. It also has a smaller "memory" (context window) compared to the paid version.

  **Gemini Advanced:** This is the only way you'd pay for the chatbot. It’s a monthly subscription (part of the Google One AI Premium plan) that gives you the "Ultra" or "Pro" models with a massive context window and better reasoning. If you haven't explicitly subscribed to this, your personal use remains **free**.

---

### 2. Moving the App to your Client

Since this is an in-house tool for a specific user, you have two main "right" ways to handle the handoff so **they** pay the bill:

**Option A: The "API Key Swap" (Easiest)**
Instead of moving the whole project, have the client create their own **Google AI Studio** account and generate their own **API Key**.

* Update your app's code (or a config file) to use *their* key instead of yours.
* This is the cleanest "clean break" because they handle their own billing and credentials entirely.

**Option B: Transferring the Project (Professional)**
If you want to keep the logs and specific project settings you've built:

1. **Invite them:** In the Google Cloud Console (or AI Studio), add the client's Gmail as an **Owner** under "IAM & Admin."
2. **The Billing Switch:** Once they accept, they go to the **Billing** section of the project and "Change Billing Account" to their own.
3. **Remove yourself:** After they’ve linked their card, they can remove you as an Owner (or you can leave the project).

---

### 3. Will your personal use now cost you?

**No.**

Adding a bank card to your **Google Cloud / Developer Console** does not turn your personal Gemini app into a paid service. They are treated as two separate "buckets":

***Bucket A (Personal):** Your chats on `gemini.google.com` or the mobile app. This is governed by your consumer account settings.
***Bucket B (Developer):** Your API usage through AI Studio. This is what uses your bank card once the "Free Tier" limits are exceeded.

> [!IMPORTANT]
> Google AI Studio has a **Free Tier** for the API as well. Even without the promotion, if your client’s usage is low (e.g., a few hundred requests a day for certain models), it might actually cost them **$0**. However, in the free tier, Google reserves the right to use that data to train their models. If the app handles sensitive medical data, your client **should** use the **Paid Tier** (Pay-as-you-go) because data in the paid tier is **not** used for training and remains private.

### Summary Table

| Service | Cost | Privacy |
| :--- | :--- | :--- |
| **Gemini App (Basic)** | Free | Standard |
| **AI Studio (Free Tier)** | Free (up to limits) | **Data may be used for training** |
| **AI Studio (Paid Tier)** | Pay-per-token | **Data is private** |

Since you're working on a medical app, I'd strongly recommend the **Paid Tier** for the client to ensure data privacy—and as we discussed, moving the billing to them is definitely the right move.

**Would you like me to help you write a small Python script to make the API key easily swappable via an environment variable or a config file?**

## Q 2

While you *could* technically add a client's card to your own account, it creates a "billing knot" that can be very difficult to untangle later. Here is why you should avoid it and how to set it up the right way.

### 1. The Risks of Putting Their Card on Your Account

If you add a client's credit card to your personal Google Cloud/AI Studio account:
***Liability:** If your account is ever compromised or flagged for a policy violation, their card is attached to that "bad" account.
***Shared Limits:** Google often sets "Quotas" (how many requests you can make per minute) at the **account level**. If you have three clients on one account, they are all fighting for the same speed limits.
**Privacy:** Since this is a **medical app**, having the client's API traffic routed through your personal developer account could raise compliance issues. It is always better for the "Data Controller" (the client) to own the account where the data is processed.

---

### 2. How to Separate Projects and Cards Properly

Google Cloud is designed to handle multiple cards for different projects. You do this by creating separate **Billing Accounts**.

#### The Setup Process

1. **Create a New Billing Account:**
    * Go to the **Billing** section in your Google Cloud Console.
    * Select "Manage Billing Accounts" and click **Create Account**.
    * Enter the client's information and **their** card details here.
2. **Create a New Project:**
    * Create a brand new "Project" specifically for this medical app.
3. **Link Them:**
    * Go to the "Billing" settings for that specific project and "Change Billing."
    * Select the **Client's Billing Account** instead of yours.
4. **Generate the API Key:**
    * Switch to that specific project in **Google AI Studio**.
    * Generate a new API key. This key is now "fueled" by the client's card, completely separate from your personal project.

---

### Comparison of Handoff Methods

| Feature | Your Card + API Key | Their Card + Your Project | Their Account (Best Practice) |
| :--- | :--- | :--- | :--- |
| **Effort** | Low | Medium | High (Initially) |
| **Security** | Poor | Medium | **Excellent** |
| **Billing Clarity** | Messy | Good | **Perfect** |
| **Ease of Exit** | Hard (You pay) | Hard (You manage) | **Easy (They own it)** |

### Why "Option A" (The Key Swap) is still the Winner

The cleanest way to handle an in-house tool is to have the client spend 5 minutes setting up their own **Google AI Studio** account.

1. They log in with their business Gmail.
2. They add their card.
3. They click "Create API Key" and send that string to you.
4. You paste that string into the app's configuration.

This ensures that **they** own the data, **they** own the bill, and if you ever stop working together, they simply revoke the key or change the password without you needing to "transfer" anything.

**Would you like me to show you how to set up an `.env` file or a simple `config.json` so the client can easily update their own API key without touching your code?**
