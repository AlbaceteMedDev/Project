"use client";

import { useState, type FormEvent } from "react";
import { site } from "@/lib/site";
import { boroughs } from "@/lib/boroughs";
import { services } from "@/lib/services";

/**
 * Visit-request form. Composes a structured email via the visitor's mail
 * client (no data is stored server-side). Swap `handleSubmit` for a POST to
 * an API route or form service when one is connected.
 */
export default function ContactForm() {
  const [sent, setSent] = useState(false);

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    const subject = encodeURIComponent(
      `Visit request — ${data.get("name")} (${data.get("borough")})`
    );
    const body = encodeURIComponent(
      [
        `Name: ${data.get("name")}`,
        `Phone: ${data.get("phone")}`,
        `Borough: ${data.get("borough")}`,
        `Wound concern: ${data.get("concern")}`,
        `Requesting care for: ${data.get("who")}`,
        "",
        `Details: ${data.get("details") || "—"}`,
      ].join("\n")
    );
    window.location.href = `mailto:${site.email}?subject=${subject}&body=${body}`;
    setSent(true);
  }

  if (sent) {
    return (
      <div className="form-sent" role="status">
        <h3>Almost there —</h3>
        <p>
          Your email draft has opened in your mail app. Press send and we&apos;ll get back
          to you promptly. Prefer the phone?{" "}
          <a href={`tel:${site.phoneHref}`}>Call {site.phone}</a> — it&apos;s often the
          fastest way to schedule.
        </p>
      </div>
    );
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label className="field">
          <span>Your name</span>
          <input name="name" type="text" required autoComplete="name" placeholder="Jane Rivera" />
        </label>
        <label className="field">
          <span>Phone number</span>
          <input
            name="phone"
            type="tel"
            required
            autoComplete="tel"
            placeholder="(718) 000-0000"
          />
        </label>
      </div>

      <div className="form-row">
        <label className="field">
          <span>Borough</span>
          <select name="borough" required defaultValue="">
            <option value="" disabled>
              Select a borough
            </option>
            {boroughs.map((b) => (
              <option key={b.slug} value={b.name}>
                {b.name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Wound concern</span>
          <select name="concern" required defaultValue="">
            <option value="" disabled>
              Select the closest match
            </option>
            {services.map((s) => (
              <option key={s.slug} value={s.shortName}>
                {s.shortName}
              </option>
            ))}
            <option value="Not sure">Not sure — need an evaluation</option>
          </select>
        </label>
      </div>

      <fieldset className="field-radios">
        <legend>Who needs care?</legend>
        <label>
          <input type="radio" name="who" value="Myself" defaultChecked /> Myself
        </label>
        <label>
          <input type="radio" name="who" value="A family member" /> A family member
        </label>
        <label>
          <input type="radio" name="who" value="A patient (I'm a provider/agency)" /> A patient
          (I&apos;m a provider)
        </label>
      </fieldset>

      <label className="field">
        <span>Anything else we should know? (optional)</span>
        <textarea
          name="details"
          rows={4}
          placeholder="How long you've had the wound, mobility considerations, insurance…"
        />
      </label>

      <button type="submit" className="btn btn-primary btn-lg form-submit">
        Send Visit Request
      </button>
      <p className="form-note">
        Please don&apos;t include detailed medical history here — we&apos;ll take it over the
        phone. For emergencies, call 911.
      </p>
    </form>
  );
}
