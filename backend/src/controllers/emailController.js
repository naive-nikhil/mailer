const { google } = require('googleapis');
const User = require('../models/User');

// Function to send email using Gmail API
const sendEmail = async (req, res) => {
    const { to, subject, message } = req.body;
    
    if (!to || !subject || !message) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    try {
        // Fetch user from DB
        const user = await User.findOne(); // Adjust query based on your auth logic

        if (!user || !user.accessToken) {
            return res.status(401).json({ error: 'User not authenticated' });
        }

        // Configure OAuth2 client
        const oAuth2Client = new google.auth.OAuth2();
        oAuth2Client.setCredentials({ access_token: user.accessToken });

        // Create Gmail API instance
        const gmail = google.gmail({ version: 'v1', auth: oAuth2Client });

        // Encode email message
        const email = [
            `To: ${to}`,
            'Content-Type: text/html; charset=utf-8',
            `Subject: ${subject}`,
            '',
            message
        ].join('\n');

        const encodedMessage = Buffer.from(email).toString('base64').replace(/\+/g, '-').replace(/\//g, '_');

        // Send email
        await gmail.users.messages.send({
            userId: 'me',
            requestBody: { raw: encodedMessage }
        });

        res.json({ success: true, message: 'Email sent successfully' });

    } catch (error) {
        console.error('Error sending email:', error);
        res.status(500).json({ error: 'Failed to send email' });
    }
};

module.exports = { sendEmail };
