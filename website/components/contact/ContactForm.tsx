'use client';

import { useState } from 'react';

const SUPPORT_EMAIL = 'support@aikahaani.com';

const inputClasses =
  'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-red-500 dark:border-white/10 dark:bg-white/[0.02] dark:text-white';

/** Frontend-only contact form. Submit opens the user's email client (mailto). */
export function ContactForm() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });

  function update(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const subject = encodeURIComponent(form.subject || `Contact from ${form.name || 'AIKahaani'}`);
    const body = encodeURIComponent(
      `Name: ${form.name}\nEmail: ${form.email}\n\n${form.message}`
    );
    window.location.href = `mailto:${SUPPORT_EMAIL}?subject=${subject}&body=${body}`;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="grid gap-5 sm:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="name" className="block text-sm font-bold text-gray-900 dark:text-white">
            Name
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            value={form.name}
            onChange={update('name')}
            placeholder="Your name"
            className={inputClasses}
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-bold text-gray-900 dark:text-white">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={form.email}
            onChange={update('email')}
            placeholder="you@example.com"
            className={inputClasses}
          />
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="subject" className="block text-sm font-bold text-gray-900 dark:text-white">
          Subject
        </label>
        <input
          id="subject"
          name="subject"
          type="text"
          value={form.subject}
          onChange={update('subject')}
          placeholder="How can we help?"
          className={inputClasses}
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="message" className="block text-sm font-bold text-gray-900 dark:text-white">
          Message
        </label>
        <textarea
          id="message"
          name="message"
          required
          rows={6}
          value={form.message}
          onChange={update('message')}
          placeholder="Tell us a bit more..."
          className={`${inputClasses} resize-y`}
        />
      </div>

      <button
        type="submit"
        className="inline-flex w-full items-center justify-center rounded-full bg-red-500 px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-red-600 sm:w-auto"
      >
        Send message
      </button>
    </form>
  );
}
