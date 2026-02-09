// Reusable CharacterCounter component
// Shows current character count with accessibility support

interface CharacterCounterProps {
  current: number;
  max: number;
  id: string;
  className?: string;
}

export function CharacterCounter({ current, max, id, className = '' }: CharacterCounterProps) {
  // Warn when approaching limit (90%+)
  const isApproachingLimit = current >= max * 0.9;
  const isOverLimit = current > max;

  const colorClass = isOverLimit
    ? 'text-red-600 font-semibold'
    : isApproachingLimit
    ? 'text-orange-500 font-medium'
    : 'text-gray-500';

  return (
    <p
      id={id}
      className={`text-xs mt-1 text-right ${colorClass} ${className}`}
      aria-live="polite"
      aria-atomic="true"
    >
      {current} / {max}
      {isOverLimit && <span className="ml-1">⚠️ Limit exceeded</span>}
    </p>
  );
}

// Usage example:
/*
import { CharacterCounter } from '@/components/ui/CharacterCounter';

const { register, watch } = useForm();
const titleLength = watch('title')?.length || 0;

<Input
  {...register('title')}
  label="Title"
  aria-describedby="title-counter"
/>
<CharacterCounter
  current={titleLength}
  max={200}
  id="title-counter"
/>
*/
