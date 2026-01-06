
import React from 'react';

export default function TermsPage() {
    return (
        <div className="container mx-auto px-4 py-12 max-w-4xl">
            <h1 className="text-4xl font-bold mb-8">Terms and Conditions</h1>
            <p className="text-sm text-muted-foreground mb-8">Last updated: January 6, 2026</p>

            <section className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">1. Introduction</h2>
                <p className="mb-4">
                    Welcome to PDF2Audiobook. By accessing our website and using our services, you agree to be bound by these Terms and Conditions.
                </p>
            </section>

            <section className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">2. Company Information</h2>
                <p className="mb-4">
                    PDF2Audiobook ("we", "us", "our") provides AI-powered PDF to audiobook conversion services.
                </p>
            </section>

            <section className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">3. Refund Policy</h2>
                <div className="p-4 border border-blue-500/20 bg-blue-500/10 rounded-lg">
                    <p className="font-medium text-blue-400 mb-2">Money-Back Guarantee</p>
                    <p>
                        We offer a full refund within <strong>14 days of purchase</strong> if you are not satisfied with our service, provided you have not used more than 20% of your purchased credits. To request a refund, please contact us at support@pdf2audiobook.xyz.
                    </p>
                </div>
            </section>

            <section className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">4. Usage & Credits</h2>
                <p className="mb-4">
                    Our services are provided on a credit basis. Credits are used to generate audio from your uploaded PDFs. Unused credits regarding subscription plans may roll over depending on your specific plan terms.
                </p>
            </section>

            <section className="mb-8">
                <h2 className="text-2xl font-semibold mb-4">5. Contact</h2>
                <p>
                    For any questions regarding these terms, please contact us at support@pdf2audiobook.xyz.
                </p>
            </section>
        </div>
    );
}
