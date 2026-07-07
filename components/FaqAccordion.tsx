"use client";

import { useState } from "react";
import type { Faq } from "@/lib/faqs";

export default function FaqAccordion({ faqs }: { faqs: Faq[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <div className="faq-list">
      {faqs.map((faq, i) => {
        const open = openIndex === i;
        return (
          <div key={faq.question} className={`faq-item ${open ? "is-open" : ""}`}>
            <h3>
              <button
                className="faq-question"
                onClick={() => setOpenIndex(open ? null : i)}
                aria-expanded={open}
                aria-controls={`faq-panel-${i}`}
              >
                <span>{faq.question}</span>
                <span className="faq-toggle" aria-hidden="true" />
              </button>
            </h3>
            <div
              id={`faq-panel-${i}`}
              className="faq-panel"
              role="region"
              aria-label={faq.question}
            >
              <div className="faq-panel-inner">
                <p>{faq.answer}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
