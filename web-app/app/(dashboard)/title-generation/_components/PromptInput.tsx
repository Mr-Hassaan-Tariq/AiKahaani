import Image from 'next/image';

import InfoIcon from '/public/images/info.svg';
import FormTextArea from 'components/ui/FormTextArea_';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function PromptInput() {
  return (
    <>
      <Row className="mt-6 flex items-center justify-start gap-2">
        <Text className="text-md mb-2 text-left text-white">What’s your video about?</Text>
        <Image className="mt-[-8px]" src={InfoIcon} alt="info-icon" width={16} height={16} />
      </Row>
      <FormTextArea
        name="prompt"
        placeholder="e.g. Top 5 productivity hacks that actually work..."
        validationSchema={{
          required: 'Prompt is required',
          minLength: { value: 30, message: 'Prompt must be at least 30 characters' },
        }}
      />
    </>
  );
}
