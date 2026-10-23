---
id: KB-010
title: Forms and Contact Workflow Patterns
domain: frontend_engineering · backend_integration · client_validation · state_management
target_agent: frontend_developer_agent
version: 1.0.0
status: approved
description: Engineering standards for building robust, type-safe interactive forms, client-side validation via Zod schemas, state lifecycle management, and secure backend submission handlers.
---

# Knowledge Base Document: KB-010
**Title:** Forms and Contact Workflow Patterns  
**Domain:** Frontend Engineering · Backend Integration · Client Validation · State Management  

---

## 1. Purpose and Operational Mandate
The primary objective of `KB-010` is to ensure that interactive data-collection points—such as client inquiry forms, booking requests, and newsletter subscriptions—are fully robust, type-safe, and secure. 

AI-generated forms frequently break because they lack error handling, depend on console logs instead of real submission paths, or omit client-side input validation. `KB-010` mandates deterministic patterns for form validation, state management, and service integration.

---

## 2. Type-Safe Validation Standard (Zod Integration)

Generated applications must validate all form inputs on both the client and server using **Zod** schema validation. Never rely on raw HTML5 validation alone.

### Example: Contact Form Zod Schema (`lib/validations.ts`)
```tsx
import { z } from 'zod';

export const contactFormSchema = z.object({
  name: z.string().min(2, { message: 'Name must be at least 2 characters long.' }),
  email: z.string().email({ message: 'Please enter a valid email address.' }),
  projectType: z.enum(['Editorial', 'Commercial', 'Portrait', 'Event', 'Other'], {
    required_error: 'Please select a project type.',
  }),
  budget: z.string().optional(),
  message: z.string().min(10, { message: 'Message must be at least 10 characters long.' }),
});

export type ContactFormValues = z.infer<typeof contactFormSchema>;

```

---

## 3. Form State Lifecycle Management

Every interactive form component (`components/contact/contact-form.tsx`) must explicitly manage four distinct submission lifecycle states to provide clear visual feedback to the user:

1. **Idle State:** Form is ready for user input; submit button is active.
2. **Submitting State:** Inputs are locked (`disabled`), and the submit button displays a loading spinner with text (e.g., *"Sending Inquiry..."*).
3. **Success State:** Form clears inputs and presents an inline confirmation success banner (e.g., *"Thank you, John will be in touch shortly."*).
4. **Error State:** Highlights invalid fields with specific error text and displays a global submission error banner if the server request fails.

---

## 4. Secure Submission Handling (Next.js Server Action Pattern)

Generated forms must submit data securely via Next.js Server Actions or trusted third-party service endpoints (e.g., Resend, Formspree, or Web3Forms) rather than unhandled client fetch requests.

### Example: Contact Form Component Implementation

```tsx
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { contactFormSchema, ContactFormValues } from '@/lib/validations';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

export function ContactForm() {
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ContactFormValues>({
    resolver: zodResolver(contactFormSchema),
  });

  const onSubmit = async (data: ContactFormValues) => {
    setStatus('submitting');
    setErrorMessage('');

    try {
      // Simulate or execute server action / endpoint submission
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error('Failed to submit inquiry.');

      setStatus('success');
      reset();
    } catch (error) {
      setStatus('error');
      setErrorMessage('Something went wrong. Please email directly at john@example.com.');
    }
  };

  if (status === 'success') {
    return (
      <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-6 text-center">
        <CheckCircle2 className="mx-auto h-10 w-10 text-emerald-500 mb-2"/>
        <h3 className="text-lg font-medium text-foreground">Inquiry Received</h3>
        <p className="text-sm text-muted-foreground mt-1">Thank you for reaching out. John will respond within 24 hours.</p>
        <Button className="mt-4" onClick="{()" variant="outline"> setStatus('idle')}>
          Send Another Message
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {status === 'error' && (
        <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          <AlertCircle className="h-5 w-5 shrink-0"/>
          <p>{errorMessage}</p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-foreground mb-2">Your Name</label>
        <input
          type="text"
          {...register('name')}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          placeholder="Jane Doe"
        />
        {errors.name && <p className="text-xs text-destructive mt-1">{errors.name.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-foreground mb-2">Email Address</label>
        <input
          type="email"
          {...register('email')}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          placeholder="jane@example.com"
        />
        {errors.email && <p className="text-xs text-destructive mt-1">{errors.email.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-foreground mb-2">Project Type</label>
        <select
          {...register('projectType')}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">Select a category...</option>
          <option value="Editorial">Editorial Shoot</option>
          <option value="Commercial">Commercial Campaign</option>
          <option value="Portrait">Portrait Session</option>
          <option value="Event">Event Coverage</option>
          <option value="Other">Other Inquiry</option>
        </select>
        {errors.projectType && <p className="text-xs text-destructive mt-1">{errors.projectType.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-foreground mb-2">Project Details & Message</label>
        <textarea
          rows={4}
          {...register('message')}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          placeholder="Describe your project scope, location, and desired timeline..."
        />
        {errors.message && <p className="text-xs text-destructive mt-1">{errors.message.message}</p>}
      </div>

      <Button 'submitting'} className="w-full" disabled="{status" type="submit">
        {status === 'submitting' && <Loader2 className="mr-2 h-4 w-4 animate-spin"/>}
        {status === 'submitting' ? 'Sending Inquiry...' : 'Send Inquiry'}
      </Button>
    </form>
  );
}

```

---

## 5. Accessibility & Guardrails

1. **Label Association:** Every form control must be explicitly linked to a `<label>` element using matching `htmlFor` and `id` attributes.
2. **Error Aria Attributes:** Invalid inputs must inject `aria-invalid="true"` and `aria-describedby` pointing directly to the validation error message container for screen readers.
3. **No Fake Consoles:** Never submit forms via `console.log` in production code. All generated forms must interface with a valid API route, server action, or third-party dispatch handler.

```
