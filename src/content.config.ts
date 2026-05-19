import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const vignettes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/vignettes' }),
  schema: z.object({
    title: z.string(),
    updated: z.coerce.date(),
    teaser: z.string(),
  }),
});

export const collections = { vignettes };
