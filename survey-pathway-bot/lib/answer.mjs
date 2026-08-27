// Turns a question (from extract.mjs) into the list of answers the bot is
// allowed to give it, and applies one of them.
//
// The candidate list is what makes pathway exploration finite: a radio with 5
// options is 5 candidates (5 branches to try), a text box is 1 candidate (no
// branch) unless the config supplies several values for it.

const DEFAULT_VALUES = {
  text: 'Test response',
  textarea: 'Automated pathway-test response.',
  number: '30',
};

function ruleFor(q, config) {
  for (const rule of config.answers ?? []) {
    const re = new RegExp(rule.match, rule.flags ?? 'i');
    if (re.test(q.key) || (q.label && re.test(q.label))) return rule;
  }
  return null;
}

function branchable(q, config) {
  if (config.branchOn) {
    const re = new RegExp(config.branchOn, 'i');
    if (!re.test(q.key) && !(q.label && re.test(q.label))) return false;
  }
  if (config.noBranch) {
    const re = new RegExp(config.noBranch, 'i');
    if (re.test(q.key) || (q.label && re.test(q.label))) return false;
  }
  return true;
}

// -> [{ kind: 'option', index, value, label } | { kind: 'value', value }]
export function candidates(q, config = {}) {
  const rule = ruleFor(q, config);

  if (q.kind === 'radio' || q.kind === 'checkbox' || q.kind === 'select') {
    let opts = q.options.map((o, index) => ({ kind: 'option', index, value: o.value, label: o.label }));
    if (rule?.options) {
      const re = new RegExp(rule.options, 'i');
      const filtered = opts.filter((o) => re.test(o.value) || re.test(o.label));
      if (filtered.length) opts = filtered;
    }
    if (rule?.skip) return [{ kind: 'noop', label: '(left unchecked)' }];
    if (rule?.fixed != null) {
      const re = new RegExp(rule.fixed, 'i');
      const hit = opts.find((o) => re.test(o.value) || re.test(o.label));
      return hit ? [hit] : opts.slice(0, 1);
    }
    // A lone checkbox is a two-way branch: ticked, or deliberately left blank.
    // (Decipher and friends name each checkbox of a multi-select separately, so
    // this is the common case, not an edge case.)
    if (q.kind === 'checkbox' && opts.length === 1 && rule?.fixed == null) {
      return branchable(q, config) ? [opts[0], { kind: 'noop', label: '(left unchecked)' }] : [opts[0]];
    }
    if (!branchable(q, config)) opts = opts.slice(0, 1);
    const cap = config.maxOptionsPerQuestion ?? 0;
    if (cap > 0 && opts.length > cap) opts = opts.slice(0, cap);
    return opts.length ? opts : [{ kind: 'noop' }];
  }

  // Free-text style.
  if (rule?.values?.length) return rule.values.map((v) => ({ kind: 'value', value: String(v) }));
  if (rule?.value != null) return [{ kind: 'value', value: String(rule.value) }];
  const fallback = config.values?.[q.kind] ?? DEFAULT_VALUES[q.kind] ?? 'Test';
  return [{ kind: 'value', value: String(fallback) }];
}

export async function apply(page, q, candidate) {
  if (candidate.kind === 'noop') return;
  if (candidate.kind === 'value') {
    await page.fill(q.selector, candidate.value);
    return;
  }
  const opt = q.options[candidate.index];
  if (!opt) throw new Error(`option ${candidate.index} missing on ${q.key}`);
  if (q.kind === 'select') {
    await page.selectOption(q.selector, opt.value);
    return;
  }
  // Radio / checkbox. Some engines overlay a styled span on the real input, so
  // fall back to a DOM click + change event when the normal check is blocked.
  try {
    await page.check(opt.selector, { timeout: 3000 });
  } catch {
    await page.evaluate((sel) => {
      const el = document.querySelector(sel);
      if (!el) return;
      el.click();
      if (!el.checked) {
        el.checked = true;
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }, opt.selector);
  }
}

export function describe(q, candidate) {
  if (candidate.kind === 'value') return `"${candidate.value}"`;
  if (candidate.kind === 'noop') return candidate.label ?? '(no answer)';
  const opt = q.options[candidate.index];
  return opt?.label ? `${opt.label} [${opt.value}]` : `[${opt?.value ?? candidate.index}]`;
}
