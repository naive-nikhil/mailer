const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Passport setup
passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: process.env.GOOGLE_CALLBACK_URL,
    scope: ['profile', 'email', 'https://www.googleapis.com/auth/gmail.send']
  },
  async (accessToken, refreshToken, profile, done) => {
    try {
      // Find or create user
      let user = await User.findOne({ googleId: profile.id });
      
      if (user) {
        // Update tokens
        user.accessToken = accessToken;
        user.refreshToken = refreshToken;
        user.tokenExpiry = new Date(Date.now() + 3600 * 1000); // Token usually expires in 1 hour
        user.updatedAt = new Date();
        await user.save();
      } else {
        // Create new user
        user = await User.create({
          googleId: profile.id,
          email: profile.emails[0].value,
          name: profile.displayName,
          picture: profile.photos[0].value,
          accessToken,
          refreshToken,
          tokenExpiry: new Date(Date.now() + 3600 * 1000)
        });
      }
      
      return done(null, user);
    } catch (error) {
      return done(error, null);
    }
  }
));

// Generate JWT for authenticated users
const generateToken = (user) => {
  return jwt.sign(
    { id: user._id, email: user.email },
    process.env.JWT_SECRET,
    { expiresIn: '7d' }
  );
};

// Export auth controller functions
module.exports = {
  authenticate: passport.authenticate('google', { 
    scope: ['profile', 'email', 'https://www.googleapis.com/auth/gmail.send'] 
  }),
  
  callback: (req, res, next) => {
    passport.authenticate('google', { session: false }, (err, user) => {
      if (err || !user) {
        return res.redirect('/auth/failure');
      }
      
      const token = generateToken(user);
      res.redirect(`/auth/success?token=${token}`);
    })(req, res, next);
  },
  
  success: (req, res) => {
    res.send('Authentication successful! You can close this window.');
  },
  
  failure: (req, res) => {
    res.status(401).send('Authentication failed. Please try again.');
  }
};