const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const emailController = require('../controllers/emailController');

// Google OAuth routes
router.get('/google', authController.authenticate);
router.get('/google/callback', authController.callback);
router.get('/success', authController.success);
router.get('/failure', authController.failure);
router.post('/send', emailController.sendEmail);
module.exports = router;