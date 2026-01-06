
import React from 'react';

export default function PrivacyPage() {
    return (
        <div className="container mx-auto px-4 py-12 max-w-4xl">
            <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
            <p className="text-sm text-muted-foreground mb-8">Last updated: January 6, 2026</p>

            <section className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">1. Data Collection</h2>
                <p className="mb-4">
                    We collect information you provide directly to us, such as when you create an account, upload files, or communicate with us. This may include your name, email address, and payment information.
                </p>
            </section>

            <section className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">2. File Security</h2>
                <p className="mb-4">
                    PDF files uploaded to our service are used solely for the purpose of generating audio. We do not share your uploaded content with third parties except as necessary to provide the service (e.g., AI processing providers).
                </p>
            </section>

            <section className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">3. Data Usage</h2>
                <p className="mb-4">
                    We use your information to provide, maintain, and improve our services, process transactions, and send you related information including confirmations and invoices.
                </p>
            </section>

            <section className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">4. Contact Us</h2>
                <p>
                    If you have any questions about this Privacy Policy, please contact us at support@pdf2audiobook.xyz.
                </p>
            </section>
        </div>
    );
}
