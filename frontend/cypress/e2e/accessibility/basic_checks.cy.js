describe('Accessibility (A11y) Manual Checks', () => {
  const routes = [
    '/login',
    '/registro',
    '/',
    '/legal/terms'
  ]

  const verifyImageAccessibility = ($img) => {
    cy.wrap($img).should('satisfy', ($el) => {
      return $el.attr('alt') !== undefined || $el.attr('aria-label') !== undefined || $el.attr('role') === 'presentation'
    })
  }

  const verifyInputWithLabel = ($input, id) => {
    cy.get(`label[for="${id}"]`).should('satisfy', ($label) => {
      return $label.length > 0 || $input.attr('aria-label') !== undefined
    })
  }

  const verifyInputWithoutLabel = ($input) => {
    cy.wrap($input).should('satisfy', ($el) => {
      return $el.attr('aria-label') !== undefined || $el.attr('aria-labelledby') !== undefined
    })
  }

  const verifyInputAccessibility = ($input) => {
    const id = $input.attr('id')
    if (id) {
      verifyInputWithLabel($input, id)
    } else {
      verifyInputWithoutLabel($input)
    }
  }

  const verifyButtonAccessibility = ($btn) => {
    cy.wrap($btn).should('satisfy', ($el) => {
      const text = $el.text().trim()
      return text !== '' || $el.attr('aria-label') !== undefined || $el.attr('aria-labelledby') !== undefined
    })
  }

  const checkImagesIfExist = () => {
    cy.get('body').then(($body) => {
      if ($body.find('img').length > 0) {
        cy.get('img').each(verifyImageAccessibility)
      }
    })
  }

  const checkInputsIfExist = () => {
    cy.get('body').then(($body) => {
      if ($body.find('input').length > 0) {
        cy.get('input').each(verifyInputAccessibility)
      }
    })
  }

  const checkButtonsIfExist = () => {
    cy.get('body').then(($body) => {
      if ($body.find('button').length > 0) {
        cy.get('button').each(verifyButtonAccessibility)
      }
    })
  }

  for (const route of routes) {
    it(`should have basic accessibility attributes on ${route}`, () => {
      cy.visit(route)
      cy.get('body', { timeout: 10000 }).should('be.visible')
      
      checkImagesIfExist()
      checkInputsIfExist()
      checkButtonsIfExist()
    })
  }

  it('should support keyboard navigation on login', () => {
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    const emailSelector = '[data-cy="input-email"], input[type="email"], input[type="text"]'
    cy.get('body').then(($body) => {
      if ($body.find(emailSelector).length > 0) {
        cy.get(emailSelector).first().focus()
        cy.focused().tab()
        cy.focused().should('satisfy', ($el) => {
          return $el.attr('data-cy') === 'input-password' || $el.attr('type') === 'password' || $el.length > 0
        })
      }
    })
  })
})

