import { Resend } from 'resend';

// POST /api/send-email
export default async function handler(req, res) {
    // Configurar CORS
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { to, subject, html } = req.body;

        if (!to || !subject || !html) {
            return res.status(400).json({ error: 'Missing required fields: to, subject, html' });
        }

        if (!process.env.RESEND_API_KEY) {
            console.error('[FATAL] Missing RESEND_API_KEY');
            return res.status(500).json({ error: 'Server config error: Missing API Key' });
        }

        const resend = new Resend(process.env.RESEND_API_KEY);
        console.log(`[DEBUG] Sending to: ${to}`);

        const { data, error } = await resend.emails.send({
            from: 'Ponte Once <onboarding@resend.dev>',
            to: [to],
            subject: subject,
            html: html
        });

        if (error) {
            console.error('[RESEND ERROR]', error);
            return res.status(400).json({ error: error.message });
        }

        console.log(`[SUCCESS] Email sent: ${data.id}`);
        return res.status(200).json({ success: true, id: data.id });

    } catch (err) {
        console.error('[EXCEPTION]', err);
        return res.status(500).json({ error: err.message });
    }
}
