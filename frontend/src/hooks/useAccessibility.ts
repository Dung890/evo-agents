import { useEffect, useCallback } from 'react'

interface UseAccessibilityOptions {
  announcePageChanges?: boolean
  manageFocus?: boolean
  enableKeyboardNavigation?: boolean
}

export const useAccessibility = (options: UseAccessibilityOptions = {}) => {
  const {
    announcePageChanges = true,
    manageFocus = true,
    enableKeyboardNavigation = true
  } = options

  // Announce page changes to screen readers
  const announceToScreenReader = useCallback((message: string) => {
    if (!announcePageChanges) return

    const announcement = document.createElement('div')
    announcement.setAttribute('aria-live', 'polite')
    announcement.setAttribute('aria-atomic', 'true')
    announcement.className = 'sr-only'
    announcement.textContent = message

    document.body.appendChild(announcement)

    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(announcement)
    }, 1000)
  }, [announcePageChanges])

  // Focus management
  const focusElement = useCallback((selector: string) => {
    if (!manageFocus) return

    const element = document.querySelector(selector) as HTMLElement
    if (element) {
      element.focus()
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [manageFocus])

  // Skip to main content
  const addSkipLink = useCallback(() => {
    const skipLink = document.createElement('a')
    skipLink.href = '#main-content'
    skipLink.textContent = 'Skip to main content'
    skipLink.className = 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-primary-600 focus:text-white focus:px-4 focus:py-2 focus:rounded-lg focus:shadow-lg'
    
    document.body.insertBefore(skipLink, document.body.firstChild)

    return () => {
      if (document.body.contains(skipLink)) {
        document.body.removeChild(skipLink)
      }
    }
  }, [])

  // Keyboard navigation helpers
  const handleKeyboardNavigation = useCallback((event: KeyboardEvent) => {
    if (!enableKeyboardNavigation) return

    // Escape key handling
    if (event.key === 'Escape') {
      const activeElement = document.activeElement as HTMLElement
      if (activeElement && activeElement.blur) {
        activeElement.blur()
      }
    }

    // Tab trapping for modals
    if (event.key === 'Tab') {
      const modal = document.querySelector('[role="dialog"]')
      if (modal) {
        const focusableElements = modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        const firstElement = focusableElements[0] as HTMLElement
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault()
          lastElement.focus()
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault()
          firstElement.focus()
        }
      }
    }
  }, [enableKeyboardNavigation])

  // Reduced motion detection
  const prefersReducedMotion = useCallback(() => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  }, [])

  // High contrast detection
  const prefersHighContrast = useCallback(() => {
    return window.matchMedia('(prefers-contrast: high)').matches
  }, [])

  // Color scheme detection
  const prefersDarkMode = useCallback(() => {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  }, [])

  useEffect(() => {
    // Add skip link
    const removeSkipLink = addSkipLink()

    // Add keyboard event listener
    document.addEventListener('keydown', handleKeyboardNavigation)

    // Cleanup
    return () => {
      removeSkipLink()
      document.removeEventListener('keydown', handleKeyboardNavigation)
    }
  }, [addSkipLink, handleKeyboardNavigation])

  return {
    announceToScreenReader,
    focusElement,
    prefersReducedMotion,
    prefersHighContrast,
    prefersDarkMode,
  }
}

// Hook for managing ARIA attributes
export const useAriaAttributes = () => {
  const setAriaLabel = useCallback((element: HTMLElement, label: string) => {
    element.setAttribute('aria-label', label)
  }, [])

  const setAriaDescribedBy = useCallback((element: HTMLElement, id: string) => {
    element.setAttribute('aria-describedby', id)
  }, [])

  const setAriaExpanded = useCallback((element: HTMLElement, expanded: boolean) => {
    element.setAttribute('aria-expanded', expanded.toString())
  }, [])

  const setAriaHidden = useCallback((element: HTMLElement, hidden: boolean) => {
    element.setAttribute('aria-hidden', hidden.toString())
  }, [])

  const setAriaLive = useCallback((element: HTMLElement, politeness: 'polite' | 'assertive' | 'off') => {
    element.setAttribute('aria-live', politeness)
  }, [])

  return {
    setAriaLabel,
    setAriaDescribedBy,
    setAriaExpanded,
    setAriaHidden,
    setAriaLive,
  }
}

// Hook for keyboard navigation
export const useKeyboardNavigation = () => {
  const handleArrowNavigation = useCallback((
    event: KeyboardEvent,
    items: NodeListOf<HTMLElement> | HTMLElement[],
    currentIndex: number,
    setCurrentIndex: (index: number) => void
  ) => {
    switch (event.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        event.preventDefault()
        const nextIndex = (currentIndex + 1) % items.length
        setCurrentIndex(nextIndex)
        ;(items[nextIndex] as HTMLElement).focus()
        break
      case 'ArrowUp':
      case 'ArrowLeft':
        event.preventDefault()
        const prevIndex = currentIndex === 0 ? items.length - 1 : currentIndex - 1
        setCurrentIndex(prevIndex)
        ;(items[prevIndex] as HTMLElement).focus()
        break
      case 'Home':
        event.preventDefault()
        setCurrentIndex(0)
        ;(items[0] as HTMLElement).focus()
        break
      case 'End':
        event.preventDefault()
        const lastIndex = items.length - 1
        setCurrentIndex(lastIndex)
        ;(items[lastIndex] as HTMLElement).focus()
        break
    }
  }, [])

  return { handleArrowNavigation }
}
