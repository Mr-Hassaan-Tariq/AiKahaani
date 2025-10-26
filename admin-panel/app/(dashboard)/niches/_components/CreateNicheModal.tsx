'use client';

import { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { Controller, FormProvider, useFieldArray, useForm } from 'react-hook-form';
import Select from 'react-select';
import { toast } from 'sonner';

import { postClientDataAction } from 'lib/utils/clientDataActions';
import Button from 'components/ui/Button';
import Dialog from 'components/ui/Dialog';
import Input from 'components/ui/FormInput';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

interface CreateNicheModalProps {
  trigger: React.ReactNode;
}

type Channel = {
  name: string;
  link: string;
};

type CardData = {
  title: string;
  description: string;
  tone: string[];
  pacing: string[];
  channels: Channel[];
  bestFor: string;
  structure: {
    intro: string;
    body: string;
    outro: string;
  };
};

const toneOptions = [
  { value: 'Neutral', label: 'Neutral' },
  { value: 'Educational', label: 'Educational' },
  { value: 'Professional', label: 'Professional' },
  { value: 'Engaging', label: 'Engaging' },
  { value: 'Conversational', label: 'Conversational' },
  { value: 'Storytelling', label: 'Storytelling' },
];

const pacingOptions = [
  { value: 'Fast', label: 'Fast' },
  { value: 'Dynamic', label: 'Dynamic' },
  { value: 'Moderate', label: 'Moderate' },
  { value: 'Slow', label: 'Slow' },
];

export default function CreateNicheModal({ trigger }: CreateNicheModalProps) {
  const [open, setOpen] = useState(false);

  const methods = useForm<CardData>({
    defaultValues: {
      title: '',
      description: '',
      tone: [],
      pacing: [],
      channels: [{ name: '', link: '' }],
      bestFor: '',
      structure: {
        intro: '',
        body: '',
        outro: '',
      },
    },
  });

  const { control, handleSubmit, reset } = methods;
  const { fields, append, remove } = useFieldArray({ control, name: 'channels' });

  const onSubmit = async (data: CardData) => {
    const payload = {
      title: data.title,
      tagline: data.description,
      tone: data.tone,
      pacing: data.pacing,
      top_channels: data.channels.filter((ch) => ch.name && ch.link),
      best_for: data.bestFor ? data.bestFor.split(',').map((s) => s.trim()) : [],
      script_structure: {
        intro: data.structure.intro,
        body: data.structure.body,
        conclusion: data.structure.outro,
      },
      status: 'active',
    };

    console.log('Sending Payload:', payload);

    try {
      const response = await postClientDataAction<any, typeof payload>('v1/admin/niches/', payload);

      console.log('API Response:', response);
      toast.success('Niche created successfully!');
      reset();
      setOpen(false);
    } catch (error: any) {
      console.error('Error creating niche:', error);
      toast.error('Failed to create niche. Please try again.');
    }
  };

  const customSelectStyles = {
    control: (base: any) => ({
      ...base,
      backgroundColor: 'rgba(255,255,255,0.1)',
      border: 'none',
      borderRadius: '0.8rem',
      padding: '2px 4px',
      boxShadow: 'none',
    }),
    menu: (base: any) => ({
      ...base,
      backgroundColor: '#f9fafb',
      borderRadius: '0.5rem',
    }),
    option: (base: any, state: { isFocused: boolean }) => ({
      ...base,
      backgroundColor: state.isFocused ? '#e5e7eb' : '#f9fafb',
      color: '#000',
    }),
  };

  return (
    <Dialog
      open={open}
      setOpen={setOpen}
      trigger={trigger}
      title="Create a Niche"
      description=""
      footer={
        <Row className="w-full gap-6">
          <Button variant="gray" onClick={() => setOpen(false)}>
            <Text
              variant="base"
              className="font-extrabold [font-feature-settings:'liga'_off,'clig'_off]"
            >
              Cancel
            </Text>
          </Button>
          <Button type="submit" variant="green" form="createNicheForm">
            Create
          </Button>
        </Row>
      }
    >
      <FormProvider {...methods}>
        <form
          id="createNicheForm"
          onSubmit={handleSubmit(onSubmit)}
          className="grid gap-6 py-5 md:grid-cols-2"
        >
          {/* Title */}
          <Input id="title" name="title" placeholder="Tech Reviews" label="Title" />

          {/* Description */}
          <Input
            id="description"
            name="description"
            type="textarea"
            placeholder="Latest tech product reviews and analysis"
            label="Tagline / Description"
          />

          {/* Script Structure */}
          <div className="md:col-span-2">
            <Text variant="base" className="mb-2 font-medium text-white">
              Script Structure
            </Text>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <Controller
                name="structure.intro"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="Intro" placeholder="Hook with latest tech trend" />
                )}
              />

              <Controller
                name="structure.body"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="Body" placeholder="Detailed review" />
                )}
              />

              <Controller
                name="structure.outro"
                control={control}
                render={({ field }) => (
                  <Input {...field} label="Conclusion" placeholder="Recommendation" />
                )}
              />
            </div>
          </div>

          {/* Best For */}
          <Input
            id="bestFor"
            name="bestFor"
            placeholder="Technology, Product Reviews, Gadgets"
            label="Best For (comma separated)"
          />

          <div></div>

          {/* Tone */}
          <div className="flex flex-col gap-2">
            <Text variant="base" className="font-medium text-white">
              Tone
            </Text>
            <Controller
              name="tone"
              control={control}
              render={({ field }) => (
                <Select
                  {...field}
                  isMulti
                  options={toneOptions}
                  placeholder="Select tone(s)"
                  onChange={(selected) => field.onChange(selected?.map((s) => s.value) || [])}
                  value={toneOptions.filter((opt) => field.value.includes(opt.value))}
                  styles={customSelectStyles}
                />
              )}
            />
          </div>

          {/* Pacing */}
          <div className="flex flex-col gap-2">
            <Text variant="base" className="font-medium text-white">
              Pacing
            </Text>
            <Controller
              name="pacing"
              control={control}
              render={({ field }) => (
                <Select
                  {...field}
                  isMulti
                  options={pacingOptions}
                  placeholder="Select pacing style(s)"
                  onChange={(selected) => field.onChange(selected?.map((s) => s.value) || [])}
                  value={pacingOptions.filter((opt) => field.value.includes(opt.value))}
                  styles={customSelectStyles}
                />
              )}
            />
          </div>

          {/* Channels */}
          <div className="md:col-span-2">
            <div className="mb-2 flex items-center justify-between">
              <Text className="text-base font-semibold text-white">Top Channels</Text>
              <button
                type="button"
                onClick={() => append({ name: '', link: '' })}
                className="flex items-center gap-1 text-sm text-green-500"
              >
                <Plus className="h-4 w-4" /> Add Channel
              </button>
            </div>

            {fields.map((field, index) => (
              <div
                key={field.id}
                className="mb-3 grid grid-cols-1 items-center gap-4 md:grid-cols-[1fr_1fr_auto]"
              >
                <Controller
                  name={`channels.${index}.name`}
                  control={control}
                  render={({ field }) => (
                    <Input {...field} label="Channel Name" placeholder="MKBHD" />
                  )}
                />

                <Controller
                  name={`channels.${index}.link`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      label="Channel Link"
                      placeholder="https://youtube.com/@mkbhd"
                    />
                  )}
                />

                <div className="mt-7 flex items-center justify-center">
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </form>
      </FormProvider>
    </Dialog>
  );
}
