# Automated Stock Analyzer - Deployment Guide

This guide provides step-by-step instructions for deploying the Automated Stock Analyzer to GitHub and Render platform.

## Prerequisites

1. **GitHub Account**: Create an account at [GitHub](https://github.com)
2. **Render Account**: Sign up at [Render](https://render.com)
3. **Python 3.8+**: Ensure Python is installed on your local machine
4. **Git**: Install Git from [https://git-scm.com/](https://git-scm.com/)

## Project Structure

```
automated-stock-analyzer/
├── analysis/              # Analysis modules (technical, fundamental, sentiment)
├── application/           # Application layer (API, alert system)
├── backtest/              # Backtesting modules
├── config/                # Configuration files
├── data_collection/       # Data collection and storage
├── data_processing/       # Data processing and feature engineering
├── prediction/            # Prediction models
├── tests/                 # Test files
├── utils/                 # Utility functions
├── visualization/         # Visualization and report generation
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── run_app.py             # Application entry point
└── DEPLOYMENT_GUIDE.md    # This deployment guide
```

## Step 1: Push Code to GitHub

1. **Initialize Git Repository** (if not already initialized):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub Repository**:
   - Go to GitHub and create a new repository named `automated-stock-analyzer`
   - Do not initialize with README, .gitignore, or license

3. **Add Remote Repository**:
   ```bash
   git remote add origin https://github.com/<your-username>/automated-stock-analyzer.git
   ```

4. **Push Code to GitHub**:
   ```bash
   git push -u origin master
   ```

## Step 2: Set Up Render PostgreSQL Database

1. **Log in to Render** and go to your dashboard
2. **Create New PostgreSQL Database**:
   - Click on "New" → "PostgreSQL"
   - Fill in the database details:
     - Name: `automated-stock-analyzer-db`
     - Region: Choose the region closest to you
     - Database: `stock_analyzer`
     - User: `stock_analyzer_user`
   - Click "Create Database"

3. **Get Database Connection String**:
   - After database creation, go to the database dashboard
   - Copy the **External Database URL** (it should look like `postgresql://user:password@hostname:port/database`)

## Step 3: Deploy Application to Render

1. **Create New Web Service**:
   - Go to Render dashboard
   - Click on "New" → "Web Service"
   - Select "GitHub" as the repository source
   - Connect to your GitHub account and select the `automated-stock-analyzer` repository
   - Click "Connect"

2. **Configure Web Service**:
   - **Name**: `automated-stock-analyzer`
   - **Region**: Same as your database region
   - **Branch**: `master`
   - **Root Directory**: Leave empty (default)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run_app.py`
   - **Environment Variables**:
     - Click on "Advanced" → "Add Environment Variable"
     - Add the following environment variables:
       | Key | Value |
       |-----|-------|
       | `DATABASE_URL` | `<your-postgresql-connection-string>` |
       | `EMAIL_SENDER` | `<your-qq-email>` |
       | `EMAIL_PASSWORD` | `<your-qq-email-authorization-code>` |
       | `EMAIL_RECIPIENT` | `<recipient-email>` |
       | `TUSHARE_TOKEN` | `<your-tushare-token>` |
   - Click "Create Web Service"

3. **Verify Deployment**:
   - Render will build and deploy your application
   - Check the logs to ensure successful deployment
   - The application should be accessible at `https://automated-stock-analyzer.onrender.com`

## Step 4: Configure Scheduling

The application uses the `schedule` library to run daily at configurable times. The default times are 6:10, 9:35, and 13:50.

To modify the schedule times:

1. Edit the `automated_analyzer_config.py` file in the `config` directory
2. Update the `SCHEDULE_TIMES` list with your desired times in HH:MM format
3. Push the changes to GitHub, and Render will automatically redeploy the application

## Step 5: Test the Application

1. **Check Logs**:
   - Go to Render dashboard → Your Web Service → Logs
   - Verify that the application is running and scheduling tasks correctly

2. **Test Email Functionality**:
   - The application will send an email report after each analysis run
   - Check your email inbox to confirm you receive the reports

3. **Monitor Database**:
   - Use a PostgreSQL client (e.g., pgAdmin, DBeaver) to connect to your Render database
   - Verify that stock data is being stored correctly

## Step 6: Set Up GitHub Actions (Optional)

To enable continuous integration and deployment:

1. Create a `.github/workflows` directory in your project
2. Create a `ci-cd.yml` file with the following content:
   ```yaml
   name: CI/CD
   
   on:
     push:
       branches: [ master ]
     pull_request:
       branches: [ master ]
   
   jobs:
     build:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v3
       - name: Set up Python 3.9
         uses: actions/setup-python@v3
         with:
           python-version: 3.9
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -r requirements.txt
       - name: Run tests
         run: |
           pytest
   ```
3. Push the changes to GitHub

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify that `DATABASE_URL` environment variable is correctly set
   - Ensure that the Render PostgreSQL database is accessible from the web service
   - Check the database firewall settings in Render

2. **Email Sending Failures**:
   - Verify QQ email settings (sender address, authorization code)
   - Ensure that the SMTP server settings are correct (smtp.qq.com, port 465 with SSL)

3. **Stock Data Collection Errors**:
   - Verify that the Tushare token is valid and has sufficient permissions
   - Check the API rate limits for Tushare

4. **Render Deployment Failures**:
   - Check the build logs for any error messages
   - Ensure that all dependencies are listed in `requirements.txt`
   - Verify that the start command is correct

### Debugging Tips

- **Check Logs**: Always start by checking the application logs in Render
- **Test Locally**: Run the application locally with the same environment variables to identify issues
- **Use Environment Variables**: Avoid hardcoding sensitive information in the code
- **Monitor Resources**: Check CPU and memory usage in Render to ensure your application has sufficient resources

## Maintenance

1. **Regular Updates**:
   - Update Python dependencies periodically
   - Monitor Tushare API changes and update the code accordingly
   - Keep the database optimized by running regular maintenance tasks

2. **Backup Strategy**:
   - Enable automatic backups for your Render PostgreSQL database
   - Consider implementing a data backup mechanism for critical stock data

3. **Performance Monitoring**:
   - Monitor application performance using Render's metrics
   - Optimize slow queries and improve data processing efficiency

4. **Security**:
   - Keep all dependencies up to date to avoid security vulnerabilities
   - Regularly rotate passwords and API keys
   - Implement proper error handling to prevent information leakage

## Conclusion

Your automated stock analyzer system is now deployed and running on Render. The system will:
1. Collect stock data daily
2. Perform comprehensive analysis (technical, fundamental, sentiment)
3. Generate HTML reports with buy/sell recommendations
4. Send reports via email at configured times
5. Store data in a PostgreSQL database

You can monitor the application through Render's dashboard and make changes to the code by pushing updates to GitHub, which will automatically trigger a redeployment on Render.
