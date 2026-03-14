import FormTextarea from 'components/ui/FormTextarea';

export default function PromptInput() {
  return (
    <div className="mt-5">
      <FormTextarea
        name="prompt"
        label="What's your video about?"
        placeholder="e.g. Top 5 productivity hacks that actually work for creators who struggle with focus…"
        validationSchema={{
          required: 'Prompt is required',
          minLength: { value: 30, message: 'Prompt must be at least 30 characters' },
        }}
        className="min-h-[100px]"
      />
    </div>
  );
}
