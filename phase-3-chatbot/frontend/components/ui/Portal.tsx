'use client';

import { useEffect, useState, ReactNode } from 'react';
import { createPortal } from 'react-dom';

interface PortalProps {
  children: ReactNode;
  /** Optional container element ID. Defaults to document.body */
  containerId?: string;
}

/**
 * Portal component for rendering children outside the DOM hierarchy.
 * Useful for modals, tooltips, and floating widgets that need to
 * escape parent overflow/z-index stacking contexts.
 */
export function Portal({ children, containerId }: PortalProps) {
  const [mounted, setMounted] = useState(false);
  const [container, setContainer] = useState<Element | null>(null);

  useEffect(() => {
    setMounted(true);

    if (containerId) {
      // Use specified container
      const el = document.getElementById(containerId);
      if (el) {
        setContainer(el);
      } else {
        console.warn(`Portal container with id "${containerId}" not found`);
        setContainer(document.body);
      }
    } else {
      // Default to document.body
      setContainer(document.body);
    }

    return () => {
      setMounted(false);
    };
  }, [containerId]);

  // Don't render on server or before mount
  if (!mounted || !container) {
    return null;
  }

  return createPortal(children, container);
}

export default Portal;
