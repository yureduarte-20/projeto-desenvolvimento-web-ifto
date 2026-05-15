/**
 * EletroService - JavaScript Application
 * Versão: 1.0
 * Data: 10/05/2026
 */

(function () {
  'use strict';

  // =====================================================
  // CONFIGURAÇÃO E UTILITÁRIOS
  // =====================================================

  const CONFIG = {
    debug: false,
    animations: {
      duration: 300,
      easing: 'ease-out'
    },
    toast: {
      duration: 5000,
      position: 'bottom-end'
    },
    validation: {
      debounce: 300
    }
  };

  // Logger utilitário
  const logger = {
    log: (...args) => CONFIG.debug && console.log('[EletroService]', ...args),
    warn: (...args) => console.warn('[EletroService]', ...args),
    error: (...args) => console.error('[EletroService]', ...args)
  };

  // Debounce utilitário
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Throttle utilitário
  function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  // =====================================================
  // MÁSCARAS DE INPUT
  // =====================================================

  const masks = {
    // Máscara de telefone: (00) 00000-0000
    phone: (value) => {
      return value
        .replace(/\D/g, '')
        .replace(/(\d{2})(\d)/, '($1) $2')
        .replace(/(\d{5})(\d)/, '$1-$2')
        .replace(/(-\d{4})\d+?$/, '$1');
    },

    // Máscara de CPF/CNPJ
    document: (value) => {
      const cleaned = value.replace(/\D/g, '');
      if (cleaned.length <= 11) {
        // CPF: 000.000.000-00
        return cleaned
          .replace(/(\d{3})(\d)/, '$1.$2')
          .replace(/(\d{3})(\d)/, '$1.$2')
          .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      } else {
        // CNPJ: 00.000.000/0000-00
        return cleaned
          .replace(/(\d{2})(\d)/, '$1.$2')
          .replace(/(\d{3})(\d)/, '$1.$2')
          .replace(/(\d{3})(\d)/, '$1/$2')
          .replace(/(\d{4})(\d{1,2})$/, '$1-$2');
      }
    },

    // Máscara de moeda (R$)
    currency: (value) => {
      return value
        .replace(/\D/g, '')
        .replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.')
        .replace(/(\d+)(\d{2})$/, 'R$ $1,$2');
    },

    // Máscara de data
    date: (value) => {
      return value
        .replace(/\D/g, '')
        .replace(/(\d{2})(\d)/, '$1/$2')
        .replace(/(\d{2})(\d)/, '$1/$2')
        .replace(/(\d{4})\d+?$/, '$1');
    }
  };

  // Aplicar máscaras em inputs
  function applyMasks() {
    document.querySelectorAll('[data-mask]').forEach(input => {
      const maskType = input.dataset.mask;
      if (masks[maskType]) {
        input.addEventListener('input', (e) => {
          e.target.value = masks[maskType](e.target.value);
        });
      }
    });
  }

  // =====================================================
  // VALIDAÇÃO DE FORMULÁRIOS
  // =====================================================

  const validators = {
    // Validação de email
    email: (value) => {
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return regex.test(value);
    },

    // Validação de senha (mínimo 6 caracteres)
    password: (value) => {
      return value.length >= 6;
    },

    // Validação de telefone
    phone: (value) => {
      const cleaned = value.replace(/\D/g, '');
      return cleaned.length >= 10 && cleaned.length <= 11;
    },

    // Validação de CPF
    cpf: (value) => {
      const cleaned = value.replace(/\D/g, '');
      if (cleaned.length !== 11) return false;

      // Validação básica de CPF (pode ser expandida)
      if (/^(\d)\1+$/.test(cleaned)) return false;

      return true;
    },

    // Validação de campo obrigatório
    required: (value) => {
      return value.trim().length > 0;
    },

    // Validação de tamanho mínimo
    minLength: (value, length) => {
      return value.length >= length;
    },

    // Validação de tamanho máximo
    maxLength: (value, length) => {
      return value.length <= length;
    }
  };

  // Validação em tempo real
  function setupValidation() {
    document.querySelectorAll('[data-validate]').forEach(input => {
      const validationType = input.dataset.validate;
      const errorMessage = input.dataset.errorMessage || 'Campo inválido';

      const validateField = debounce(() => {
        const isValid = validators[validationType](input.value);

        if (!isValid && input.value.length > 0) {
          input.classList.add('is-invalid');
          input.classList.remove('is-valid');

          // Mostrar mensagem de erro
          let feedback = input.parentElement.querySelector('.invalid-feedback');
          if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            input.parentElement.appendChild(feedback);
          }
          feedback.textContent = errorMessage;
        } else if (input.value.length > 0) {
          input.classList.add('is-valid');
          input.classList.remove('is-invalid');
        } else {
          input.classList.remove('is-valid', 'is-invalid');
        }
      }, CONFIG.validation.debounce);

      input.addEventListener('input', validateField);
      input.addEventListener('blur', validateField);
    });
  }

  // =====================================================
  // NAVEGAÇÃO E ACESSIBILIDADE
  // =====================================================

  // Skip link
  function setupSkipLink() {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link';
    skipLink.textContent = 'Pular para conteúdo principal';
    document.body.insertBefore(skipLink, document.body.firstChild);
  }

  // Navegação por teclado
  function setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
      // Escape para fechar modais
      if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
          const closeButton = openModal.querySelector('[data-bs-dismiss="modal"]');
          if (closeButton) closeButton.click();
        }
      }
    });
  }

  // Atalhos de teclado
  function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + N: Nova OS
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const newOrderLink = document.querySelector('a[href*="create"]');
        if (newOrderLink) newOrderLink.click();
      }

      // Ctrl/Cmd + F: Foco no search
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="search"]');
        if (searchInput) searchInput.focus();
      }
    });
  }

  // =====================================================
  // TOAST NOTIFICATIONS
  // =====================================================

  function showToast(message, type = 'success', duration = CONFIG.toast.duration) {
    // Container de toasts
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
      document.body.appendChild(toastContainer);
    }

    // Criar toast
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    const iconMap = {
      success: 'check-circle',
      danger: 'exclamation-triangle',
      warning: 'exclamation-circle',
      info: 'info-circle'
    };

    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi bi-${iconMap[type]} me-2"></i>${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    `;

    toastContainer.appendChild(toast);

    // Mostrar toast
    const bsToast = new bootstrap.Toast(toast, { delay: duration });
    bsToast.show();

    // Remover do DOM após esconder
    toast.addEventListener('hidden.bs.toast', () => {
      toast.remove();
    });
  }

  // =====================================================
  // COPY TO CLIPBOARD
  // =====================================================

  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      showToast('Link copiado para a área de transferência!', 'success');
    } catch (err) {
      logger.error('Erro ao copiar:', err);
      showToast('Erro ao copiar. Tente selecionar e copiar manualmente.', 'danger');
    }
  }

  // =====================================================
  // CONFIRMAÇÕES
  // =====================================================

  function confirmAction(message, callback) {
    if (confirm(message)) {
      callback();
    }
  }

  // =====================================================
  // INICIALIZAÇÃO
  // =====================================================

  function init() {
    logger.log('Inicializando EletroService...');

    // Configurações de acessibilidade
    setupSkipLink();
    setupKeyboardNavigation();
    setupKeyboardShortcuts();

    // Máscaras e validação
    applyMasks();
    setupValidation();

    // Expor funções globais
    window.EletroService = {
      showToast,
      copyToClipboard,
      confirmAction,
      masks,
      validators
    };

    logger.log('EletroService inicializado com sucesso!');
  }

  // Inicializar quando DOM estiver pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
