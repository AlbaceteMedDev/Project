import Link from "next/link";
import Emblem from "@/components/Emblem";

export default function NotFound() {
  return (
    <section className="notfound">
      <div className="container">
        <Emblem size={80} className="notfound-emblem" />
        <h1>This page has healed over.</h1>
        <p>
          The address you followed doesn&apos;t exist anymore — but the care does.
        </p>
        <Link href="/" className="btn btn-primary">
          Back to Apollo Wound Care
        </Link>
      </div>
    </section>
  );
}
