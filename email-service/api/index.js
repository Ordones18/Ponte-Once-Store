import { Hono } from 'hono'
import { handle } from 'hono/vercel'
import { cors } from 'hono/cors'
import nodemailer from 'nodemailer'

const app = new Hono().basePath('/api')

app.use('/*', cors())

app.get('/', (c) => c.text('Email Service is Running! 🚀'))

app.post('/send-email', async (c) => {
    try {
        console.log('[DEBUG] Received email request');
        const body = await c.req.json()
        const { to, subject, html } = body

        if (!to || !subject || !html) {
            console.log('[ERROR] Missing fields');
            return c.json({ error: 'Missing required fields: to, subject, html' }, 400)
        }

        console.log(`[DEBUG] Preparing to send email to: ${to}`);

        // Verificar variables (sin imprimir la contraseña)
        if (!process.env.MAIL_USERNAME || !process.env.MAIL_PASSWORD) {
            console.error('[FATAL] Missing MAIL_USERNAME or MAIL_PASSWORD env variables');
            return c.json({ error: 'Server configuration error: Missing credentials' }, 500);
        }

        const transporter = nodemailer.createTransport({
            service: 'gmail',
            auth: {
                user: process.env.MAIL_USERNAME,
                pass: process.env.MAIL_PASSWORD
            }
        })

        console.log('[DEBUG] Transporter created. Sending mail...');

        const info = await transporter.sendMail({
            from: process.env.MAIL_USERNAME,
            to,
            subject,
            html
        })

        console.log(`[SUCCESS] Email sent. MessageID: ${info.messageId}`);
        return c.json({ success: true, messageId: info.messageId })
    } catch (error) {
        console.error('[ERROR] Email sending failed:', error)
        return c.json({ error: error.message }, 500)
    }
})

export default handle(app)
