import ScriptSelector from './ScriptSelector';
import Col from 'components/ui/Col';
import FormInput from 'components/ui/FormInput';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function OptimizeFormFields({ watch, scripts, register }: any) {
  return (
    <Col className="mt-6 w-full justify-start gap-4">
      <Text className="text-md mb-2 text-left text-white">Script length & duration</Text>
      <Row className="flex flex-col items-start justify-start gap-4 lg:flex-row lg:gap-[200px]">
        <label className="flex cursor-pointer items-center gap-2">
          <input
            type="radio"
            value="saved"
            {...register('duration')}
            className="peer h-6 w-6 cursor-pointer appearance-none rounded-full border-2 border-[#AAACA6] checked:border-white checked:bg-white checked:shadow-[inset_0_0_0_4px_#1E1E1E]"
          />
          <Text className="text-[16px] text-[#AAACA6] peer-checked:text-white">
            Use a saved draft or script
          </Text>
        </label>
        <label className="flex cursor-pointer items-center gap-2">
          <input
            type="radio"
            value="manual"
            {...register('duration')}
            className="peer h-6 w-6 cursor-pointer appearance-none rounded-full border-2 border-[#AAACA6] checked:border-white checked:bg-white checked:shadow-[inset_0_0_0_4px_#1E1E1E]"
          />
          <Text className="text-[16px] text-[#AAACA6] peer-checked:text-white">
            Enter a title manually
          </Text>
        </label>
      </Row>

      {watch('duration') === 'saved' && (
        <ScriptSelector
          name="scriptOption"
          scripts={(scripts ?? []).map((s: any) => ({
            uuid: String(s.uuid),
            title: s.title,
            outline_title: s.outline_title,
          }))}
        />
      )}

      {watch('duration') === 'manual' && (
        <FormInput
          name="manualTitle"
          placeholder="Enter your title manually..."
          validationSchema={{
            required: 'Title is required when entering manually',
            minLength: { value: 10, message: 'Title must be at least 5 characters' },
          }}
        />
      )}
    </Col>
  );
}
