/**
 * Frontend Configuration
 * Switch between local development and production API
 */

const CONFIG = {
    // Environment detection
    isDevelopment: window.location.hostname === 'localhost' ||
                   window.location.hostname === '127.0.0.1' ||
                   window.location.hostname === '',

    // API URLs
    API_URL_LOCAL: 'http://localhost:8000',
    API_URL_PRODUCTION: 'https://your-backend-url.railway.app',  // Update when backend is deployed

    // Get current API URL based on environment
    get API_URL() {
        return this.isDevelopment ? this.API_URL_LOCAL : this.API_URL_PRODUCTION;
    },

    // Backend deployment options
    BACKEND_OPTIONS: {
        railway: {
            name: 'Railway',
            url: 'https://railway.app',
            freeTier: true,
            setup: 'Easy - Connect GitHub, auto-deploy',
            pros: ['Free tier', 'Auto-deploy from GitHub', 'Simple setup'],
            cons: ['500 hours/month free limit']
        },
        render: {
            name: 'Render',
            url: 'https://render.com',
            freeTier: true,
            setup: 'Easy - Connect GitHub, configure',
            pros: ['Free tier', 'Good for APIs', 'Auto-deploy'],
            cons: ['Spins down after inactivity (slow cold starts)']
        },
        googleCloudRun: {
            name: 'Google Cloud Run',
            url: 'https://cloud.google.com/run',
            freeTier: true,
            setup: 'Medium - Needs Docker configuration',
            pros: ['Free tier (2M requests/month)', 'You already have Google credentials', 'Scales to zero'],
            cons: ['Requires Docker', 'More setup']
        },
        flyio: {
            name: 'Fly.io',
            url: 'https://fly.io',
            freeTier: true,
            setup: 'Medium - CLI tool + Docker',
            pros: ['Good free tier', 'Fast global deployment'],
            cons: ['Requires Docker']
        },
        local: {
            name: 'Local (with ngrok)',
            url: 'https://ngrok.com',
            freeTier: true,
            setup: 'Quick - Run locally, expose with ngrok',
            pros: ['No deployment needed', 'Good for testing'],
            cons: ['Computer must be running', 'Not permanent']
        }
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
