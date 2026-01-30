import { Hono } from 'hono'
import { handle } from 'hono/vercel'
import { cors } from 'hono/cors'
import nodemailer from 'nodemailer'

const app = new Hono().basePath('/api')

app.use('/*', cors())

app.get('/', (c) => c.text('Email Service is Running! 🚀'))

app.post('/send-email', async (c) => {
    try {
        const body = await c.req.json()
        const { to, subject, html } = body

        if (!to || !subject || !html) {
            return c.json({ error: 'Missing required fields: to, subject, html' }, 400)
        }

        const transporter = nodemailer.createTransport({
            service: 'gmail',
            auth: {
                user: process.env.MAIL_USERNAME,
                pass: process.env.MAIL_PASSWORD
            }
        })

        const info = await transporter.sendMail({
            from: process.env.MAIL_USERNAME,
            to,
            subject,
            html
        })

        return c.json({ success: true, messageId: info.messageId })
    } catch (error) {
        console.error('Email error:', error)
        return c.json({ error: error.message }, 500)
    }
})

export default handle(app)
