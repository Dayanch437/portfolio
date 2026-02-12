interface AvatarProps {
  imageUrl: string | null;
  altText: string;
}

export default function Avatar({ imageUrl, altText }: AvatarProps) {
  return (
    <div className="hero__intro">
      {imageUrl && (
        <img
          className="avatar"
          src={imageUrl}
          alt={altText}
        />
      )}
    </div>
  );
}
