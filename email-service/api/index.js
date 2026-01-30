import { Hono } from 'hono'
import { handle } from 'hono/vercel'
import { cors } from 'hono/cors'
import { Resend } from 'resend'

const app = new Hono()

app.use('/*', cors())

app.get('/api', (c) => c.text('Email Service (Resend) is Running! 🚀'))
app.get('/api/', (c) => c.text('Email Service (Resend) is Running! 🚀'))

app.post('/api/send-email', async (c) => {
    try {
        const body = await c.req.json()
        const { to, subject, html } = body

        if (!to || !subject || !html) {
            return c.json({ error: 'Missing required fields' }, 400)
        }

        if (!process.env.RESEND_API_KEY) {
            console.error('[FATAL] Missing RESEND_API_KEY');
            return c.json({ error: 'Server config error' }, 500);
        }

        const resend = new Resend(process.env.RESEND_API_KEY);

        console.log(`[DEBUG] Sending via Resend to: ${to}`);

        const { data, error } = await resend.emails.send({
            from: 'Ponte Once <onboarding@resend.dev>', // Domain de prueba de Resend
            to: [to],
            subject: subject,
            html: html
        });

        if (error) {
            console.error('[RESEND ERROR]', error);
            return c.json({ error: error.message }, 400);
        }

        console.log(`[SUCCESS] Email sent: ${data.id}`);
        return c.json({ success: true, id: data.id });

    } catch (error) {
        console.error('[ERROR] Exception:', error)
        return c.json({ error: error.message }, 500)
    }
})

export default handle(app)
