import Image from 'next/image';

import EditIcon from '/public/images/edit.svg';
import RefreshIcon from '/public/images/refresh.svg';
import Row from 'components/ui/Row';
import Text from 'components/ui/Text';

export default function ActionButtons({ isGenerating, onEdit, onRegenerate }: any) {
  return (
    <Row className="flex w-full gap-3">
      <button
        onClick={onEdit}
        className="flex flex-1 items-center justify-center gap-2 rounded-[100px] bg-[#FFFFFF1A] py-[18px]"
      >
        <Image src={EditIcon} alt="edit-icon" width={24} height={24} />
        <Text className="text-[16px] font-bold text-white">Edit Title Info</Text>
      </button>
      <button
        onClick={onRegenerate}
        disabled={isGenerating}
        className="flex flex-1 items-center justify-center gap-2 rounded-[100px] bg-[#FFFFFF1A] py-[18px]"
      >
        {isGenerating ? (
          <>
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
            <Text className="text-[16px] font-bold text-white">Regenerating...</Text>
          </>
        ) : (
          <>
            <Image src={RefreshIcon} alt="refresh-icon" width={24} height={24} />
            <Text className="text-[16px] font-bold text-white">Regenerate</Text>
          </>
        )}
      </button>
    </Row>
  );
}
